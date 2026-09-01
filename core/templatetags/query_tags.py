from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    request = context.get("request")
    if request is None:
        return "?"
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is None or value == "":
            params.pop(key, None)
        else:
            params[key] = value
    encoded = params.urlencode()
    return f"?{encoded}" if encoded else "?"
