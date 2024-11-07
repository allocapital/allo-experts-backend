from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Mechanism

class MechanismAdmin(admin.ModelAdmin):
    filter_horizontal = ('experts', 'builds', 'courses')

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["slug"].help_text = "This field is automatically generated"
        return form

    list_display = ('title', 'created_at', 'slug')
    search_fields = ('title', 'description', 'slug')

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

    def get_related_objects(self, mechanism):
            related_objects = []
            object_types = {
                'course': mechanism.courses.all(),
                'expert': mechanism.experts.all(),
                'build': mechanism.builds.all(),
            }

            for obj_type, queryset in object_types.items():
                for obj in queryset:
                    title = obj.name if obj_type == 'expert' else obj.title
                    url = f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/change/"
                    related_objects.append({
                        'type': obj_type,
                        'instance': obj, 
                        'id': obj.id,
                        'title': title,
                        'url': url
                    })
                   

            return related_objects
    
    def get_related_data(self, mechanism):
        related_objects = self.get_related_objects(mechanism)
    
        return {
            'mechanism': mechanism,
            'related_objects': related_objects,
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
        node_ids = set()
        edge_ids = set()

        # Function to add an undirected edge if it doesn't already exist
        def add_edge(node_from, node_to, edges_js, edge_ids):
            edge = tuple(sorted([node_from, node_to]))  # Sorts nodes to ensure consistent ordering
            # Check if the edge already exists in either direction
            if edge not in edge_ids:
                edges_js.append(f"{{ from: '{edge[0]}', to: '{edge[1]}' }}")
                edge_ids.add(edge) 

        # Define colors for node types
        colors = {
            'mechanism': '#1f78b4',  # Blue
            'course': '#33a02c',      # Green
            'build': '#e31a1c',       # Red
            'expert': '#ff7f00'       # Orange
        }

        # Mechanism Node
        mechanism_id = f"mechanism_{related_data['mechanism'].id}"
        nodes_js.append(f"{{ id: '{mechanism_id}', label: '{related_data['mechanism'].title}', shape: 'dot', size: 60, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors['mechanism']}', title: '/admin/{related_data['mechanism']._meta.app_label}/{related_data['mechanism']._meta.model_name}/{related_data['mechanism'].id}/change/' }}")
        node_ids.add(mechanism_id)

        # Direct Relationships
        # Loop through all related objects to create nodes and edges
        for obj in related_data['related_objects']:
            obj_id = f"{obj['type']}_{obj['id']}"
            
            if obj_id not in node_ids:
                nodes_js.append(
                    f"{{ id: '{obj_id}', label: '{obj['title']}', shape: 'dot', size: 26, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors[obj['type']]}', title: '/admin/{obj['instance']._meta.app_label}/{obj['instance']._meta.model_name}/{obj['instance'].id}/change/' }}"
                )
                node_ids.add(obj_id)

            # Add edge between mechanism and the related object
            add_edge(mechanism_id, obj_id, edges_js, edge_ids)
        
        all_types = ['mechanism', 'expert', 'course', 'build']
        
        # Level 2 Relationships: Connect related objects to each other as needed (e.g. experts, courses, builds)
        for obj in related_data['related_objects']:
            obj_id = f"{obj['type']}_{obj['id']}"

            print("level2 objectId: ", obj_id)
            # e.g: expert.mechanisms, expert.courses, expert.builds
            for related_type in all_types:
                if related_type != obj['type']:  # Skip the same type
                    
                    # Dynamically fetch the related items
                    related_items = getattr(obj['instance'], f"{related_type}s").all()
                    print("level2 object related_type: ", related_type)
                    # e.g: for each expert.mechanisms item
                    for related_item in related_items:
                        related_item_id = f"{related_type}_{related_item.id}"
                        print("level2 object related_item_id: ", related_item_id)
                        # Dynamically calculate the color based on type
                        color = colors[related_type]
                        
                        # Add the related item as a node if it doesn't already exist
                        if related_item_id not in node_ids:
                            label = getattr(related_item, 'title', getattr(related_item, 'name', ''))
                            nodes_js.append(
                                f"{{ id: '{related_item_id}', label: '{label}', shape: 'dot', size: 26, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors[related_type]}', title: '/admin/{related_item._meta.app_label}/{related_item._meta.model_name}/{related_item.id}/change/' }}"
                            )
                            node_ids.add(related_item_id)
                        
                        # Add the edge to the graph
                        add_edge(obj_id, related_item_id, edges_js, edge_ids)

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

            // Click event listener for nodes
            network.on('click', function (event) {{
                var nodeId = event.nodes[0]; // Get the ID of the clicked node
                if (nodeId) {{
                    var node = nodes.get(nodeId);
                    var url = node.title; // Get the URL from the node's title
                    window.open(url, '_blank'); // Open the URL in a new tab
                }}
            }});
        </script>
        """
        return script



admin.site.register(Mechanism, MechanismAdmin)
