
from django.shortcuts import render
from django.http import HttpResponse
from experts.models import Expert 


# global graph
def get_global_graph_script(self, related_data):
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
            'expert': '#ff7f00' ,      # Orange
            'category': '#ffffff'       # White
        }

        all_types = ['mechanism', 'expert', 'course', 'build', 'category']


        # Recursive function to traverse related objects
        def traverse(instance, instance_type, visited):
            instance_id = f"{instance_type}_{instance.id}"
            # Check if this node was already visited to prevent infinite loops
            if instance_id in visited:
                return
            visited.add(instance_id)
            # Add main node
            if instance_id not in node_ids:
                color = colors.get(instance_type, '#888888')
                label = getattr(instance, 'title', getattr(instance, 'name', ''))
                nodes_js.append(
                    f"{{ id: '{instance_id}', label: '{label}', shape: 'dot', size: 60, "
                    f"font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, "
                    f"color: '{color}', title: '/admin/{instance._meta.app_label}/{instance._meta.model_name}/{instance.id}/change/' }}"
                )
                node_ids.add(instance_id)

            # Go through each type to find related objects except the current type
            for related_type in all_types:
                    if related_type == 'category':
                        related_model_name = 'categories'
                    else:
                        related_model_name = f"{related_type}s" 
                    
                    if hasattr(instance, related_model_name):
                        related_items = getattr(instance, related_model_name).all()
                        
                        for related_item in related_items:
                            related_item_id = f"{related_type}_{related_item.id}"
                            related_color = colors.get(related_type, '#888888')
                            
                            # Add node for related item if it hasn't been added
                            if related_item_id not in node_ids:
                                related_label = getattr(related_item, 'title', getattr(related_item, 'name', ''))
                                nodes_js.append(
                                    f"{{ id: '{related_item_id}', label: '{related_label}', shape: 'dot', size: 26, "
                                    f"font: {{ size: 20, color: '#ffffff', face: 'arial', strokeWidth: 0, strokeColor: '#000000' }}, "
                                    f"color: '{related_color}', title: '/admin/{related_item._meta.app_label}/{related_item._meta.model_name}/{related_item.id}/change/' }}"
                                )
                                node_ids.add(related_item_id)

                            if instance_id != related_item_id:
                              # Add an undirected edge if it doesn't already exist
                              edge = tuple(sorted([instance_id, related_item_id]))
                              if edge not in edge_ids:
                                  edges_js.append(f"{{ from: '{edge[0]}', to: '{edge[1]}' }}")
                                  edge_ids.add(edge)
                              
                              # Recursively traverse related items
                              traverse(related_item, related_type, visited)

        # Start traversal from the main instance
        main_instance = related_data['instance']
        main_instance_type = main_instance._meta.model_name
        traverse(main_instance, main_instance_type, visited=set())


        script = f"""
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <div id="mynetwork" style="width: 100%; height: 600px;" "></div>
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

def visual_map(request):
    related_object_types = {
        'course': 'courses',
        'mechanism': 'mechanisms',
        'build': 'builds',
        'expert': 'experts',
        'category': 'categories',
    }
    
    # Fetch the initial instance to start the graph rendering (e.g., the first mechanism, expert, etc.)
    instance = Expert.objects.get(id=1)
    related_object_types = {}

    def get_related_objects(instance):
            related_objects = []

            for obj_type, related_name in related_object_types.items():
                related_queryset = getattr(instance, related_name).all()
                for obj in related_queryset:
                    title = getattr(obj, 'name', getattr(obj, 'title', ''))
                    url = f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/change/"
                    related_objects.append({
                        'type': obj_type,
                        'instance': obj, 
                        'id': obj.id,
                        'title': title,
                        'url': url
                    })
            return related_objects
    
    def get_related_data(instance):
        related_objects = get_related_objects(instance)
        return {
            'instance': instance,
            'related_objects': related_objects,
        }
    
    related_data = get_related_data(instance)
    script = get_global_graph_script(instance, related_data) 

    # Render the template and pass the script as context
    return render(request, 'admin/visual_map.html', {
        'graph_script': script
    })
