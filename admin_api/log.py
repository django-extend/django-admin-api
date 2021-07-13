from django.contrib.admin.options import get_content_type_for_model

def log_addition(request, object, message):
    """
    Log that an object has been successfully added.

    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import LogEntry, ADDITION
    return LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(object).pk,
        object_id=object.pk,
        object_repr=str(object),
        action_flag=ADDITION,
        change_message=message,
    )

def log_change(request, object, message):
    """
    Log that an object has been successfully changed.

    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import LogEntry, CHANGE
    return LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(object).pk,
        object_id=object.pk,
        object_repr=str(object),
        action_flag=CHANGE,
        change_message=message,
    )

def log_deletion(request, object, object_repr):
    """
    Log that an object will be deleted. Note that this method must be
    called before the deletion.

    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import LogEntry, DELETION
    return LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(object).pk,
        object_id=object.pk,
        object_repr=object_repr,
        action_flag=DELETION,
    )