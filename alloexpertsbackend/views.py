
from django.shortcuts import render
from django.http import HttpResponse
from experts.models import Expert 
from django.http import JsonResponse


def get_global_graph_data(instance):
    nodes = []
    edges = []
    node_ids = set()
    edge_ids = set()

    # Define colors and groups
    colors = {
        'mechanism': '#1f78b4',
        'course': '#33a02c',
        'build': '#e31a1c',
        'expert': '#ff7f00',
        'category': '#ffffff'
    }
    groups = {
        'mechanism': 'Mechanisms',
        'course': 'Courses',
        'build': 'Builds',
        'expert': 'Experts',
        'category': 'Categories'
    }

    def traverse(instance, instance_type, visited):
        instance_id = f"{instance_type}_{instance.id}"
        if instance_id in visited:
            return
        visited.add(instance_id)

        # Add node
        if instance_id not in node_ids:
            nodes.append({
                "id": instance_id,
                "label": getattr(instance, 'title', getattr(instance, 'name', '')),
                "group": groups.get(instance_type, 'Other'),
                "color": colors.get(instance_type, '#888888'),
                "url": f"/admin/{instance._meta.app_label}/{instance._meta.model_name}/{instance.id}/change/"
            })
            node_ids.add(instance_id)

        # Traverse related objects
        for related_type in ['mechanism', 'expert', 'course', 'build', 'category']:
            related_name = f"{related_type}s" if related_type != 'category' else 'categories'
            if hasattr(instance, related_name):
                for related_item in getattr(instance, related_name).all():
                    related_item_id = f"{related_type}_{related_item.id}"

                    # 
                    edges.append({"source": instance_id, "target": related_item_id})
                    traverse(related_item, related_type, visited)

    traverse(instance, instance._meta.model_name, set())
    return {"nodes": nodes, "edges": edges}


def visual_map(request):
    instance = Expert.objects.get(id=1)  # Replace with a dynamic instance fetch
    graph_data = get_global_graph_data(instance)
    return JsonResponse(graph_data)
