from django.contrib import admin
from django.shortcuts import render
from django.urls import path

class GraphAdmin(admin.ModelAdmin):

    related_object_types = {}

    def get_related_objects(self, instance):
            related_objects = []

            for obj_type, related_name in self.related_object_types.items():
                related_queryset = getattr(instance, related_name).all()
                for obj in related_queryset:
                    title = getattr(obj, 'name', getattr(obj, 'title', ''))
                    # title = obj.name if obj_type == 'expert' else obj.title
                    url = f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/change/"
                    related_objects.append({
                        'type': obj_type,
                        'instance': obj, 
                        'id': obj.id,
                        'title': title,
                        'url': url
                    })
            return related_objects

    def get_related_data(self, instance):
        related_objects = self.get_related_objects(instance)
        return {
            'instance': instance,
            'related_objects': related_objects,
        }

    def change_view(self, request, object_id, form_url='', extra_context=None):
        instance = self.get_object(request, object_id)
        related_data = self.get_related_data(instance)

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

        # Get the main instance (e.g., mechanism, course, etc.)
        instance = related_data['instance']
        instance_type = instance._meta.model_name
        instance_id = f"{instance_type}_{instance.id}"
        color = colors.get(instance_type, '#888888')
        title = getattr(instance, 'name', getattr(instance, 'title', ''))

        # Main Instance Node
        nodes_js.append(f"{{ id: '{instance_id}', label: '{title}', shape: 'dot', size: 60, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{color}', title: '/admin/{instance._meta.app_label}/{instance._meta.model_name}/{instance.id}/change/' }}")
        node_ids.add(instance_id)

        # Direct Relationships
        # Loop through all related objects to create nodes and edges
        for obj in related_data['related_objects']:
            obj_id = f"{obj['type']}_{obj['id']}"

            if obj_id not in node_ids:
                nodes_js.append(
                    f"{{ id: '{obj_id}', label: '{obj['title']}', shape: 'dot', size: 26, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors[obj['type']]}', title: '/admin/{obj['instance']._meta.app_label}/{obj['instance']._meta.model_name}/{obj['instance'].id}/change/' }}"
                )
                node_ids.add(obj_id)

            # Add edge between instance and the related object
            add_edge(instance_id, obj_id, edges_js, edge_ids)

        # Level 2 Relationships
        all_types = ['mechanism', 'expert', 'course', 'build']
        
        
        # Level 2 Relationships: Connect related objects to each other as needed (e.g. experts, courses, builds)

        # Level 2 Relationships: Connect related objects to each other as needed (e.g. experts, courses, builds)
        for obj in related_data['related_objects']:
            obj_id = f"{obj['type']}_{obj['id']}"

            for related_type in all_types:
                if related_type != obj['type']:  # Skip the same type
                    
                    # Dynamically fetch the related items
                    related_items = getattr(obj['instance'], f"{related_type}s").all()

                    for related_item in related_items:
                        related_item_id = f"{related_type}_{related_item.id}"
                        color = colors[related_type]
                        
                        
                        # Add the related item as a node if it doesn't already exist

                        # Add the related item as a node if it doesn't already exist
                        if related_item_id not in node_ids:
                            label = getattr(related_item, 'title', getattr(related_item, 'name', ''))
                            nodes_js.append(
                                f"{{ id: '{related_item_id}', label: '{label}', shape: 'dot', size: 26, font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, color: '{colors[related_type]}', title: '/admin/{related_item._meta.app_label}/{related_item._meta.model_name}/{related_item.id}/change/' }}"
                            )
                            node_ids.add(related_item_id)
                        
                        
                        # Add the edge to the graph

                        # Add the edge to the graph
                        add_edge(obj_id, related_item_id, edges_js, edge_ids)

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
                        highlight: '#D3D3D3',
                        hover: 'white'
                    }},
                    length: 300,
                    smooth: false //straight lines
                }},
                interaction: {{
                    zoomView: true,
                    zoomSpeed: 0.2,
                    dragView: true,
                    selectable: true
                }},
                physics: {{
                enabled: true,
                barnesHut: {{
                    gravitationalConstant: -20000,
                    centralGravity: 0.1,
                    springLength: 100,
                    springConstant: 0.04
                }},
                repulsion: {{
                    nodeDistance: 100,
                    springLength: 200
                }},
                solver: 'barnesHut',  // Use Barnes-Hut solver for better layout
                timestep: 0.5
            }},
             layout: {{
                improvedLayout: true,  // Use improved layout to enhance graph structure
                randomSeed: 2,  // Fix the randomness of the layout
                hierarchicalRepulsion: {{
                    centralGravity: 0.1,
                    springLength: 200,
                    springConstant: 0.01,
                    nodeDistance: 150
                }}
            }},
            }};
            var network = new vis.Network(container, data, options);

            // Add click event listener for nodes
            network.on('click', function (event) {{
                var nodeId = event.nodes[0];
                if (nodeId) {{
                    var node = nodes.get(nodeId);
                    var url = node.title;
                    window.open(url, '_blank');
                }}
            }});
        </script>
        """
        return script
