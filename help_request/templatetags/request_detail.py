from django import template

register = template.Library()


@register.inclusion_tag('request_detail_for_list.html')
def request_detail(cur_request):
    return {'current_request': cur_request}
