from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.http import JsonResponse

class GraphAdmin(admin.ModelAdmin):
    related_object_types = {
        'mechanism': 'mechanisms',
        'expert': 'experts',
        'build': 'builds',
        'course': 'courses',
        'category': 'categories',
    }

    def get_related_objects(self, instance, depth=0, max_depth=2, visited=None):
        if visited is None:
            visited = set()
        
        instance_id = f"{instance._meta.model_name}_{instance.id}"
        if instance_id in visited:
            return []

        visited.add(instance_id)
        related_objects = []

        # Get direct relationships (Level 1)
        for obj_type, related_name in self.related_object_types.items():
            if hasattr(instance, related_name):
                related_queryset = getattr(instance, related_name).all()
                for obj in related_queryset:
                    obj_id = f"{obj_type}_{obj.id}"
                    if obj_id not in visited:
                        title = getattr(obj, 'name', getattr(obj, 'title', ''))
                        related_objects.append({
                            'type': obj_type,
                            'instance': obj,
                            'id': obj.id,
                            'title': title,
                            'url': f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/change/"
                        })

                        # If at level 1, get relationships from those objects (Level 2)
                        if depth == 0:
                            for sub_type, sub_related_name in self.related_object_types.items():
                                if hasattr(obj, sub_related_name):
                                    sub_queryset = getattr(obj, sub_related_name).all()
                                    for sub_obj in sub_queryset:
                                        sub_id = f"{sub_type}_{sub_obj.id}"
                                        if sub_id not in visited:
                                            sub_title = getattr(sub_obj, 'name', getattr(sub_obj, 'title', ''))
                                            related_objects.append({
                                                'type': sub_type,
                                                'instance': sub_obj,
                                                'id': sub_obj.id,
                                                'title': sub_title,
                                                'url': f"/admin/{sub_obj._meta.app_label}/{sub_obj._meta.model_name}/{sub_obj.id}/change/"
                                            })
                                            visited.add(sub_id)

        return related_objects

    def get_graph_data(self, instance):
        nodes = []
        edges = []
        node_ids = set()
        edge_ids = set()

        colors = {
            'mechanism': '#1f78b4',
            'course': '#33a02c',
            'build': '#e31a1c',
            'expert': '#ff7f00',
            'category': '#ffffff'
        }

        def add_node(obj, obj_type, is_main=False):
            node_id = f"{obj_type}_{obj.id}"
            if node_id not in node_ids:
                title = getattr(obj, 'name', getattr(obj, 'title', ''))
                nodes.append({
                    "id": node_id,
                    "label": title,
                    "color": colors.get(obj_type, '#888888'),
                    "type": obj_type,
                    "url": f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/change/",
                    "isMain": is_main
                })
                node_ids.add(node_id)
            return node_id

        def check_direct_relation(obj1, obj2):
            # Check if obj2 is in any of obj1's related fields
            for _, related_name in self.related_object_types.items():
                if hasattr(obj1, related_name):
                    related_items = getattr(obj1, related_name).all()
                    if obj2 in related_items:
                        return True
            return False

        def add_edge(source_obj, target_obj, source_id, target_id):
            if check_direct_relation(source_obj, target_obj):
                edge_id = tuple(sorted([source_id, target_id]))
                if edge_id not in edge_ids:
                    edges.append({
                        "source": edge_id[0],
                        "target": edge_id[1]
                    })
                    edge_ids.add(edge_id)

        # Add main instance node
        instance_type = instance._meta.model_name
        main_node_id = add_node(instance, instance_type, True)

        # Get all related objects
        related_objects = self.get_related_objects(instance)

        # Add level 1 nodes and edges
        level1_nodes = []
        for obj in related_objects:
            related_node_id = add_node(obj['instance'], obj['type'])
            if check_direct_relation(instance, obj['instance']):
                level1_nodes.append(obj)
                add_edge(instance, obj['instance'], main_node_id, related_node_id)

        # Add edges between related nodes only if they have direct relationships
        for i, obj1 in enumerate(related_objects):
            node1_id = f"{obj1['type']}_{obj1['id']}"
            for obj2 in related_objects[i+1:]:
                node2_id = f"{obj2['type']}_{obj2['id']}"
                add_edge(obj1['instance'], obj2['instance'], node1_id, node2_id)

        # Prepare groups data
        groups = []
        category_nodes = [n for n in nodes if n["type"] == "category"]
        
        for cat_node in category_nodes:
            category_related = [
                node for node in nodes
                if any(
                    (edge["source"] == cat_node["id"] and edge["target"] == node["id"]) or
                    (edge["target"] == cat_node["id"] and edge["source"] == node["id"])
                    for edge in edges
                )
            ]
            if category_related:
                groups.append({
                    "category": cat_node,
                    "nodes": category_related,
                    "edges": edges
                })

        uncategorized = [
            node for node in nodes
            if node["type"] != "category" and
            not any(node in group["nodes"] for group in groups)
        ]

        return {
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
            "uncategorized": uncategorized
        }


    def get_graph_view_context(self, request, object_id):
        instance = self.get_object(request, object_id)
        if instance:
            return {
                'title': str(instance),
                'graph_data': self.get_graph_data(instance)
            }
        return None

    def graph_data_view(self, request, object_id):
        context = self.get_graph_view_context(request, object_id)
        if context:
            return JsonResponse(context['graph_data'])
        return JsonResponse({"error": "Object not found"}, status=404)

    def network_view(self, request, object_id):
        context = self.get_graph_view_context(request, object_id)
        if context:
            return render(request, 'admin/courses/course/change_form.html', {
                **self.get_changeform_initial_data(request),
                'title': context['title'],
                'graph_data': context['graph_data'],
                'original': self.get_object(request, object_id),
            })
        return JsonResponse({"error": "Object not found"}, status=404)