from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from models import Favorite
from forms import DeleteFavoriteForm
from django.http import HttpResponse
from django.utils import simplejson

@login_required
def ajax_add_favorite(request):
    """ Adds favourite returns Http codes"""
    if request.method == "POST":
        object_id = request.POST.get("object_id")
        content_type=get_object_or_404(ContentType, pk=request.POST.get("content_type_id"))
        obj = content_type.get_object_for_this_type(pk=object_id)

        # check if it was created already
        if Favorite.objects.filter(content_type=content_type, object_id=object_id,\
                                  user=request.user):
            # return conflict response code if already satisfied
            return HttpResponse(status=409)
        
        #if not create it
        favorite = Favorite.objects.create_favorite(obj, request.user)
        count = Favorite.objects.favorites_for_object(obj).count()
        return HttpResponse(simplejson.dumps({'count': count}),
                            'application/javascript',
                            status=200)
    else:
        return HttpResponse(status=405)
        
        
@login_required
def ajax_remove_favorite(request):
    """ Adds favourite returns Http codes"""
    if request.method == "POST":
        object_id = request.POST.get("object_id")
        content_type=get_object_or_404(ContentType,
                                       pk=request.POST.get("content_type_id"))
        favorite = get_object_or_404(Favorite, object_id=object_id,
                                               content_type=content_type,
                                               user=request.user)
        favorite.delete()
        obj = content_type.get_object_for_this_type(pk=object_id)
        count = Favorite.objects.favorites_for_object(obj).count()
        return HttpResponse(simplejson.dumps({'count': count}),
                            'application/javascript',
                            status=200)
    else:
        return HttpResponse(status=405)
    
    
@login_required
def create_favorite(request, object_id, queryset, redirect_to=None,
        template_name=None, extra_context=None):
    """
    Generic `add to favorites` view

    `queryset` - required for content object retrieving
    `redirect_to` is set to `favorites` by default - change it if needed

    Raises Http404 if content object does not exist.

    Example of usage (urls.py):
        url(r'favorites/add/(?P<object_id>\d+)/$', 
            'favorites.views.create_favorite', kwargs={
                'queryset': MyModel.objects.all(),
            }, name='add-to-favorites')
        
    """
    obj = get_object_or_404(queryset, pk=object_id)
    content_type=ContentType.objects.get_for_model(obj)

    if Favorite.objects.filter(content_type=content_type, object_id=object_id,\
                              user=request.user):
        return redirect(redirect_to or 'favorites')

    favorite = Favorite.objects.create_favorite(obj, request.user)
    return redirect(redirect_to or 'favorites')


@login_required
def delete_favorite(request, object_id, form_class=None, redirect_to=None,
           template_name=None, extra_context=None):
    """
    Generic Favorite object delete view

    GET: displays question to delete favorite
    POST: deletes favorite object and returns to `redirect_to`

    Default context:
        `form` - delete form

    `object_id` - required object_id (favorite pk)
    `template_name` - default "favorites/favorite_delete.html"
    `form_class` - default DeleteFavoriteForm
    `redirect_to` - default set to "favorites", change it if needed
    `extra_context` - provide extra context if needed
    """

    favorite = get_object_or_404(Favorite, pk=object_id, user=request.user)
    form_class = form_class or DeleteFavoriteForm

    if request.method == 'POST':
        form = form_class(instance=favorite, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(redirect_to or 'favorites')
    else:
        form = form_class(instance=favorite)
    ctx = extra_context or {}
    ctx.update({
        'form': form,
    })

    return render_to_response(template_name or 'favorites/favorite_delete.html',
            RequestContext(request, ctx))

@login_required
def drop_favorite(request, object_id, redirect_to=None):
    Favorite.objects.filter(pk=object_id, user=request.user).delete()
    return redirect(redirect_to or request.META.get('HTTP_REFERER', 'favorites'))
