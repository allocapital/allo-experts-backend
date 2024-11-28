# views.py
from django.shortcuts import render
from django.http import JsonResponse
from experts.models import Expert

# views.py
def get_global_graph_data(instance):
    nodes = []
    edges = []
    node_ids = set()
    edge_ids = set()
    node_categories = {}  # Track category assignments for nodes
    
    colors = {
        'mechanism': '#1f78b4',
        'course': '#33a02c',
        'build': '#e31a1c',
        'expert': '#ff7f00',
        'category': '#ffffff'
    }

    def traverse(instance, instance_type, visited):
        instance_id = f"{instance_type}_{instance.id}"
        if instance_id in visited:
            return
        visited.add(instance_id)

        # Create node data
        node_data = {
            "id": instance_id,
            "label": getattr(instance, 'title', getattr(instance, 'name', '')),
            "type": instance_type,
            "color": colors.get(instance_type, '#888888'),
            "url": f"/admin/{instance._meta.app_label}/{instance._meta.model_name}/{instance.id}/change/"
        }

        # Add node if not already present
        if instance_id not in node_ids:
            nodes.append(node_data)
            node_ids.add(instance_id)

        # Traverse related objects and build relationships
        for related_type in ['mechanism', 'expert', 'course', 'build', 'category']:
            related_name = f"{related_type}s" if related_type != 'category' else 'categories'
            if hasattr(instance, related_name):
                for related_item in getattr(instance, related_name).all():
                    related_id = f"{related_type}_{related_item.id}"

                    # Track category relationships
                    if related_type == 'category':
                        if instance_type != 'category':
                            if instance_id not in node_categories:
                                node_categories[instance_id] = []
                            node_categories[instance_id].append(related_id)
                    
                    # Add edge
                    edge_id = tuple(sorted([instance_id, related_id]))
                    if edge_id not in edge_ids:
                        edges.append({
                            "source": instance_id,
                            "target": related_id
                        })
                        edge_ids.add(edge_id)

                    traverse(related_item, related_type, visited)

    # Start traversal
    traverse(instance, instance._meta.model_name, set())

    # Prepare groups view data
    groups_data = []
    category_nodes = [node for node in nodes if node["type"] == "category"]
    non_category_nodes = [node for node in nodes if node["type"] != "category"]

    # Create groups data including all nodes and their relationships
    for cat_node in category_nodes:
        category_nodes_list = [
            node for node in non_category_nodes 
            if node['id'] in node_categories and cat_node['id'] in node_categories[node['id']]
        ]
        
        if category_nodes_list:  # Only create groups for categories that have nodes
            group_data = {
                "category": cat_node,
                "nodes": category_nodes_list,
                "edges": edges  # Include all edges to show inter-node connections
            }
            groups_data.append(group_data)

    # Add uncategorized nodes to all groups to maintain connections
    uncategorized_nodes = [
        node for node in non_category_nodes 
        if node['id'] not in node_categories
    ]

    return {
        "nodes": nodes,  # All nodes including categories
        "edges": edges,
        "groups": groups_data,
        "uncategorized": uncategorized_nodes
    }

def visual_map(request):
    """
    View function that renders the visual graph data.
    Fetches a starting instance and returns the graph data as JSON.
    """
    try:
        # Try to get first expert, or handle empty database appropriately
        instance = Expert.objects.first()
        if not instance:
            return JsonResponse({"nodes": [], "edges": [], "groups": []})
        
        # Get graph data starting from this instance
        graph_data = get_global_graph_data(instance)
        return JsonResponse(graph_data)
    
    except Expert.DoesNotExist:
        return JsonResponse({"nodes": [], "edges": [], "groups": []})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def admin_visual_page(request):
    """
    View function that renders the admin visual page template.
    """
    return render(request, 'admin/visual_map.html')