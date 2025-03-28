import os
import datetime
import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

# Try to import BigQuery, but handle the case when it's not installed
try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

from mechanisms.models import Mechanism, MechanismMapping, MechanismTrend

class Command(BaseCommand):
    help = 'Fetches funding data from BigQuery, applies mapping rules, and updates trend data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--months',
            type=int,
            default=6,
            help='Number of months of data to fetch (default: 6)'
        )
        parser.add_argument(
            '--mock',
            action='store_true',
            help='Use mock data instead of fetching from BigQuery'
        )
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Clear all existing trend data for the mechanisms being updated'
        )

    def handle(self, *args, **options):
        # Check if BigQuery is installed
        if bigquery is None and not options['mock']:
            self.stderr.write(self.style.ERROR(
                "The Google Cloud BigQuery library is not installed. "
                "Please install it with:\n\n"
                "    pip install google-cloud-bigquery\n\n"
                "Or run with --mock to use mock data instead."
            ))
            sys.exit(1)
            
        months = options['months']
        self.stdout.write(f'Fetching funding data for the last {months} months...')
        
        # Calculate the start date (first day of the month, N months ago)
        today = timezone.now().date()
        start_date = datetime.date(today.year, today.month, 1) - datetime.timedelta(days=1)
        for _ in range(months - 1):
            start_date = (start_date.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
        
        # Format the start date for BigQuery
        start_date_str = start_date.strftime('%Y-%m-%d')
        
        try:
            # Fetch data from BigQuery or use mock data
            if options['mock']:
                raw_data = self.generate_mock_data(start_date)
                self.stdout.write(self.style.WARNING('Using mock data instead of BigQuery'))
            else:
                raw_data = self.fetch_from_bigquery(start_date_str)
            
            # Apply mapping rules and aggregate data
            trend_data = self.process_data(raw_data)
            
            # Update the database
            self.update_database(trend_data, options['clear_all'])
            
            self.stdout.write(self.style.SUCCESS('Successfully updated trend data!'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating trend data: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def generate_mock_data(self, start_date):
        """
        Generates mock funding data for testing.
        Returns a list of dictionaries with month, funder, grant_pool_name, and total_usd.
        """
        self.stdout.write('Generating mock data...')
        
        # Define some sample funders and grant pools
        funders = [
            ('gitcoin', ['grants-round-1', 'grants-round-2', 'grants-round-3']),
            ('optimism', ['retroactive-funding', 'public-goods']),
            ('arbitrumfoundation', ['grants']),
            ('opencollective', ['open-source']),
            ('stellar', ['community-fund']),
            ('octant-golemfoundation', ['glm-experiment']),
        ]
        
        # Generate data for each month
        data = []
        current_date = start_date
        today = timezone.now().date()
        
        while current_date <= today:
            # For each funder and grant pool
            for funder, grant_pools in funders:
                for grant_pool in grant_pools:
                    # Generate a random funding amount (between 50k and 500k)
                    import random
                    amount = random.randint(50000, 500000)
                    
                    data.append({
                        'month': current_date,
                        'funder': funder,
                        'grant_pool_name': grant_pool,
                        'total_usd': amount
                    })
            
            # Move to the next month
            if current_date.month == 12:
                current_date = datetime.date(current_date.year + 1, 1, 1)
            else:
                current_date = datetime.date(current_date.year, current_date.month + 1, 1)
        
        self.stdout.write(f'Generated {len(data)} mock records')
        return data
    
    def fetch_from_bigquery(self, start_date):
        """
        Fetches funding data from BigQuery.
        Returns a list of dictionaries with month, funder, grant_pool_name, and total_usd.
        """
        self.stdout.write('Connecting to BigQuery...')
        
        # Initialize BigQuery client
        client = bigquery.Client()
        
        # Define the query
        query = f"""
            SELECT
                DATE_TRUNC(time, MONTH) as month,
                from_project_name as funder,
                grant_pool_name,
                SUM(amount) as total_usd
            FROM `arched-osprey-422811-e6.oso_production.oss_funding_v0`
            WHERE time >= '{start_date}'
            GROUP BY 1, 2, 3
            ORDER BY 1 DESC
        """
        
        self.stdout.write('Running BigQuery query...')
        query_job = client.query(query)
        results = query_job.result()
        
        # Convert to list of dictionaries
        data = []
        for row in results:
            data.append({
                'month': row.month.date(),  # Convert to Python date
                'funder': row.funder,
                'grant_pool_name': row.grant_pool_name,
                'total_usd': row.total_usd
            })
        
        self.stdout.write(f'Fetched {len(data)} records from BigQuery')
        return data
    
    def process_data(self, raw_data):
        """
        Applies mapping rules to categorize funding by mechanism.
        Returns a dictionary with (mechanism_id, month) as keys and total_usd as values.
        Unmapped funding is aggregated into an "Other" category.
        """
        self.stdout.write('Applying mapping rules...')
        
        # Get all mapping rules
        mappings = list(MechanismMapping.objects.select_related('mechanism').all())
        
        # Get or create the "Other" mechanism for unmapped funding
        other_mechanism, created = Mechanism.objects.get_or_create(
            title="Other",
            defaults={
                'description': "Funding that doesn't have a specific mechanism mapping",
                'slug': 'other',
                'background_color': '#FFFDEB',
                'hidden': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created "Other" mechanism for unmapped funding'))
        else:
            # Ensure it's hidden even if it already existed
            if not other_mechanism.hidden:
                other_mechanism.hidden = True
                other_mechanism.save()
                self.stdout.write(self.style.SUCCESS('Updated existing "Other" mechanism to be hidden'))
        
        # Initialize result dictionary
        trend_data = {}
        
        # Track unmapped funders for creating mappings
        unmapped_funders = set()
        
        # Process each record
        for record in raw_data:
            month = record['month']
            funder = record['funder']
            grant_pool_name = record['grant_pool_name']
            total_usd = record['total_usd']
            
            # Find the matching mapping rule
            mechanism = self.find_matching_mechanism(mappings, funder, grant_pool_name)
            
            if mechanism:
                # Add to the trend data for the mapped mechanism
                key = (mechanism.id, month)
                if key in trend_data:
                    trend_data[key] += total_usd
                else:
                    trend_data[key] = total_usd
            else:
                # Add to the trend data for the "Other" mechanism
                key = (other_mechanism.id, month)
                if key in trend_data:
                    trend_data[key] += total_usd
                else:
                    trend_data[key] = total_usd
                
                unmapped_funders.add(funder)
                
                self.stdout.write(self.style.WARNING(
                    f'No mapping found for funder="{funder}", grant_pool="{grant_pool_name}" - adding to "Other" category'
                ))
        
        self.create_mappings_for_unmapped_funders(unmapped_funders, other_mechanism)
        
        self.stdout.write(f'Processed data into {len(trend_data)} trend records')
        return trend_data

    def create_mappings_for_unmapped_funders(self, unmapped_funders, other_mechanism):
        """
        Creates general MechanismMapping entries for unmapped funders, mapping them to the "Other" mechanism.
        Creates one entry per funder with no grant pool name specified.
        """
        if not unmapped_funders:
            return
        
        created_count = 0
        for funder in unmapped_funders:
            # Check if a general mapping already exists for this funder
            existing = MechanismMapping.objects.filter(
                funder=funder,
                grant_pool_name__isnull=True
            ).exists()
            
            if not existing:
                MechanismMapping.objects.create(
                    funder=funder,
                    grant_pool_name=None, 
                    mechanism=other_mechanism,
                    priority=0 
                )
                created_count += 1
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(
                f'Created {created_count} new general mappings for unmapped funders to the "Other" category'
            ))

    def find_matching_mechanism(self, mappings, funder, grant_pool_name):
        """
        Find the matching mechanism for a funder and grant pool.
        First tries to find an exact match for both funder and grant pool.
        If no exact match is found, tries to find a match for just the funder.
        Returns None if no match is found.
        
        The mappings are sorted by priority (highest first) to ensure that
        higher priority mappings take precedence.
        """
        # Sort mappings by priority (highest first)
        sorted_mappings = sorted(mappings, key=lambda m: -m.priority)
        
        # First, try to find an exact match for both funder and grant pool
        for mapping in sorted_mappings:
            if mapping.funder.lower() == funder.lower() and mapping.grant_pool_name and mapping.grant_pool_name.lower() == grant_pool_name.lower():
                return mapping.mechanism
        
        # If no exact match is found, try to find a match for just the funder
        for mapping in sorted_mappings:
            if mapping.funder.lower() == funder.lower() and not mapping.grant_pool_name:
                return mapping.mechanism
        
        # If no match is found, return None
        return None
    
    
    @transaction.atomic
    def update_database(self, trend_data, clear_all=False):
        """
        Updates the MechanismTrend table with the new data.
        Uses a transaction to ensure data consistency.
        
        Args:
            trend_data: Dictionary with (mechanism_id, month) as keys and total_usd as values
            clear_all: If True, delete ALL trend data regardless of mechanism
        """
        self.stdout.write('Updating database...')
        
        # Get the mechanisms and months we're updating
        months = set(month for _, month in trend_data.keys())
        mechanisms = set(mech_id for mech_id, _ in trend_data.keys())
        
        if clear_all:
            # Delete ALL trend data regardless of mechanism
            self.stdout.write(self.style.WARNING('Deleting ALL trend data (--clear-all)'))
            deleted_count = MechanismTrend.objects.all().delete()[0]
        else:
            # Only delete data for the specific mechanisms and months
            delete_filter = {
                'mechanism_id__in': mechanisms,
                'month__in': months
            }
            self.stdout.write('Deleting data only for the specific mechanisms and months being updated')
            deleted_count = MechanismTrend.objects.filter(**delete_filter).delete()[0]
        
        if deleted_count > 0:
            self.stdout.write(f'Deleted {deleted_count} existing trends')
        
        # Track counts for reporting
        created_count = 0
        
        # Create new trends with the updated data
        for (mechanism_id, month), value in trend_data.items():
            MechanismTrend.objects.create(
                mechanism_id=mechanism_id,
                month=month,
                value=value
            )
            created_count += 1
        
        self.stdout.write(f'Created {created_count} new trends with fresh data')