from backend.services.pipeline_templates import python_pipeline, node_pipeline


def generate_pipeline(project_type):
    if project_type == "python":
        return python_pipeline
    if project_type == "node":
        return node_pipeline

    return None
