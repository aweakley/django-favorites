from django.contrib.sessions.models import Session
from django.db import models, connection
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class FavoriteManager(models.Manager):
    """ A Manager for Favorites
    """

    def favourites_for_session(self, session):
        return self.get_query_set().filer(session=session)

    def favorites_for_model(self, model, session=None):
        """ Returns Favorites for a specific model
        """
        content_type = ContentType.objects.get_for_model(model)
        qs = self.get_query_set().filter(content_type=content_type)
        if session:
            qs = qs.filter(session=session)
        return qs

    def favorites_for_object(self, obj, session=None):
        """ Returns Favorites for a specific object
        """
        content_type = ContentType.objects.get_for_model(type(obj))
        qs = self.get_query_set().filter(content_type=content_type, 
                                         object_id=obj.pk)
        if session:
            qs = qs.filter(session=session)

        return qs

    def favorites_for_objects(self, object_list, session=None):
        """
        Get a dictionary mapping object ids to favorite
        of votes for each object.
        """
        object_ids = [o.pk for o in object_list]
        if not object_ids:
            return {}

        content_type = ContentType.objects.get_for_model(object_list[0])

        qs = self.get_query_set().filter(content_type=content_type,
                                         object_id__in=object_ids)
        counters = qs.values('object_id').annotate(count=models.Count('object_id'))
        results = {}
        for c in counters:
            results.setdefault(c['object_id'], {})['count'] = c['count']
            results.setdefault(c['object_id'], {})['is_favorite'] = False
            results.setdefault(c['object_id'], {})['content_type_id'] = content_type.id
        if session:
            qs = qs.filter(session=session)
            for f in qs:
                results.setdefault(f.object_id, {})['is_favorite'] = True

        return results

    def favorite_for_session(self, obj, session):
        """Returns the favorite, if exists for obj by session
        """
        content_type = ContentType.objects.get_for_model(type(obj))
        return self.get_query_set().get(content_type=content_type,
                                    session=session, object_id=obj.pk)

    @classmethod
    def create_favorite(cls, content_object, session):
        content_type = ContentType.objects.get_for_model(type(content_object))
        favorite = Favorite(
            session=session,
            content_type=content_type,
            object_id=content_object.pk,
            content_object=content_object
            )
        favorite.save()
        return favorite

class Favorite(models.Model):
    session = models.ForeignKey(Session)
    content_type = models.ForeignKey(ContentType)
    object_id = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    created_on = models.DateTimeField(auto_now_add=True)
    
    objects = FavoriteManager()

    class Meta:
        verbose_name = _('favorite')
        verbose_name_plural = _('favorites')
        unique_together = (('user', 'content_type', 'object_id'),)
    
    def __unicode__(self):
        return u"%s likes %s" % (self.user, self.content_object)

@receiver(models.signals.post_delete)
def remove_favorites(sender, **kwargs):
    instance = kwargs.get('instance')
    Favorite.objects.favorites_for_object(instance).delete()
