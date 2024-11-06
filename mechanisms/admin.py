from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Mechanism

class MechanismAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('network/<int:object_id>/', self.admin_site.admin_view(self.network_view), name='mechanism_network'),
        ]
        return custom_urls + urls

    def network_view(self, request, object_id):
        mechanism = self.get_object(request, object_id)
        related_data = self.get_related_data(mechanism)
        return render(request, 'allo-experts-backend/mechanisms/mechanism/change_form.html', {
            'data': related_data,
            'original': mechanism,
            'graph_script': self.get_graph_script(related_data),
        })

    def get_related_data(self, mechanism):
         # Direct relationships (Level 1)
        related_courses = list(mechanism.courses.all())
        related_experts = list(mechanism.experts.all())
        related_builds = list(mechanism.builds.all())

        return {
            'mechanism': mechanism,
            'related_courses': related_courses,
            'related_experts': related_experts,
            'related_builds': related_builds,
        }


    def change_view(self, request, object_id, form_url='', extra_context=None):
        mechanism = self.get_object(request, object_id)
        related_data = self.get_related_data(mechanism)

        extra_context = extra_context or {}
        extra_context['network_data'] = related_data
        extra_context['graph_script'] = self.get_graph_script(related_data)

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_graph_script(self, related_data):
        nodes_js = []
        edges_js = []
        node_ids = set()  # Track node IDs to avoid duplicates

        # Define colors for node types
        colors = {
            'mechanism': '#1f78b4',  # Blue
            'course': '#33a02c',      # Green
            'build': '#e31a1c',       # Red
            'expert': '#ff7f00'       # Orange
        }

        # Mechanism Node
        mechanism_id = f"mechanism_{related_data['mechanism'].id}"
        nodes_js.append(f"{{ id: '{mechanism_id}', label: '{related_data['mechanism'].title}', shape: 'dot', size: 40, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors['mechanism']}' }}")
        node_ids.add(mechanism_id)

        # Direct Relationships
        for course in related_data['related_courses']:
            course_id = f"course_{course.id}"
            nodes_js.append(f"{{ id: '{course_id}', label: '{course.title}', shape: 'dot', size: 26, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors['course']}' }}")
            node_ids.add(course_id)
            edges_js.append(f"{{ from: '{mechanism_id}', to: '{course_id}' }}")

        for expert in related_data['related_experts']:
            expert_id = f"expert_{expert.id}"
            nodes_js.append(f"{{ id: '{expert_id}', label: '{expert.name}', shape: 'dot', size: 26, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors['expert']}' }}")
            node_ids.add(expert_id)
            edges_js.append(f"{{ from: '{mechanism_id}', to: '{expert_id}' }}")

        for build in related_data['related_builds']:
            build_id = f"build_{build.id}"
            node_ids.add(build_id)
            nodes_js.append(f"{{ id: '{build_id}', label: '{build.title}', shape: 'dot', size: 26, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors['build']}' }}")
            edges_js.append(f"{{ from: '{mechanism_id}', to: '{build_id}' }}")

        # Level 2 Relationships for Experts
        for expert in related_data['related_experts']:

            # experts.mechanisms
            # Ensure this is a relationship to a mechanism and not a duplicate
            for related_mechanism in expert.mechanisms.all():
                if related_mechanism != related_data['mechanism']:  # Avoid self-loop
                    related_mechanism_id = f"mechanism_{related_mechanism.id}"
                    # Check if the node ID is already in node_ids
                    if related_mechanism_id not in node_ids:
                        # If the node does not exist, add it
                        nodes_js.append(
                            f"{{ id: '{related_mechanism_id}', label: '{related_mechanism.title}', shape: 'dot', size: 26, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors['mechanism']}' }}"
                        )
                        node_ids.add(related_mechanism_id)
                    # Add the edge regardless of whether the node was new or already existed
                    edges_js.append(f"{{ from: 'expert_{expert.id}', to: '{related_mechanism_id}' }}")

            # experts.courses
            # Ensure this is a relationship to a mechanism and not a duplicate
            for related_course in expert.courses.all():  # Assuming Expert model has courses
                related_course_id = f"course_{related_course.id}"
                # Check if the node ID is already in node_ids
                if related_course_id not in node_ids:
                        # If the node does not exist, add it
                        nodes_js.append(
                            f"{{ id: '{related_course_id}', label: '{related_course.title}', shape: 'dot', size: 26, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors['course']}' }}"
                        )
                        node_ids.add(related_course_id)
                    # Add the edge regardless of whether the node was new or already existed
                edges_js.append(f"{{ from: 'expert_{expert.id}', to: '{related_course_id}' }}")
                

            # experts.builds
            # Ensure this is a relationship to a mechanism and not a duplicate
            for related_build in expert.builds.all():  # Assuming Expert model has builds
                related_build_id = f"build_{related_build.id}"
                # Check if the node ID is already in node_ids
                if related_build_id not in node_ids:
                        # If the node does not exist, add it
                        nodes_js.append(
                            f"{{ id: '{related_build_id}', label: '{related_build.title}', shape: 'dot', size: 26, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors['build']}' }}"
                        )
                        node_ids.add(related_build_id)
                    # Add the edge regardless of whether the node was new or already existed
                edges_js.append(f"{{ from: 'expert_{expert.id}', to: '{related_build_id}' }}")
                    

        print("Nodes: %s", nodes_js)
        print("Edges: %s", edges_js)

        # Final graph script
        script = f"""
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <div id="mynetwork" style="width: 100%; height: 600px;"></div>
        <script>
            var nodes = new vis.DataSet([{', '.join(nodes_js)}]);
            var edges = new vis.DataSet([{', '.join(edges_js)}]);
            var container = document.getElementById('mynetwork');
            var data = {{ nodes: nodes, edges: edges }};
            var options = {{  
                edges: {{
                    color: {{
                        color: '#D3D3D3',  
                        highlight: '#D3D3D3', // Highlight color when hovered
                        hover: 'white' // Color when hovered
                    }},
                    length: 300 // Adjust length
                }},
                interaction: {{
                    zoomView: true,    
                    zoomSpeed: 0.5,    // Adjust the zoom speed; default is 1
                    dragView: true,    
                    selectable: true    
                }}
            }};
            var network = new vis.Network(container, data, options);
        </script>
        """
        return script



admin.site.register(Mechanism, MechanismAdmin)
