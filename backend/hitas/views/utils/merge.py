from typing import Any, Callable, Dict, List, TypeVar

ExistingObject = TypeVar("ExistingObject")


def merge_model(model_class, existing_qs, wanted, create_defaults, equal_fields):
    def create_fn(**kwargs):
        model_class.objects.create(**{**create_defaults, **kwargs})

    def equal_fn(existing: ExistingObject, wanted: Dict[str, Any]):
        for field in equal_fields:
            if getattr(existing, field) != wanted[field]:
                return False
        return True

    def save_fn(existing, wanted_object) -> None:
        for key, value in wanted_object.items():
            setattr(existing, key, value)
        existing.save()

    def delete_fn(instances: List[ExistingObject]) -> None:
        model_class.objects.filter(pk__in=map(lambda instance: instance.pk, instances)).delete()

    merge(
        existing_objects=list(existing_qs),
        wanted_objects=wanted,
        create_fn=create_fn,
        equal_fn=equal_fn,
        save_fn=save_fn,
        delete_fn=delete_fn,
    )


def merge(
    existing_objects: list[ExistingObject],
    wanted_objects: list[Dict[str, Any]],
    create_fn: Callable[[Any], None],
    equal_fn: Callable[[ExistingObject, Dict[str, Any]], bool],
    save_fn: Callable[[ExistingObject, Dict[str, Any]], None],
    delete_fn: Callable[[List[ExistingObject]], None],
) -> None:
    """
    Merge function that tries to minimize database writes. Useful when there's a list of (sub)objects that do not have a
    dedicated identifier (improvements, ownerships...).

     - First it tries to find existing objects so no writes to those objects happen
     - Secondly it tries to reuse old objects that should be removed (UPDATE)
     - Only if there's more wanted objects than existing ones then new ones are created (INSERT)
     - Finally if there was less wanted objects than existing ones then unwanted objects are removed (DELETE)
    """

    not_found = []

    # Try to find an existing match for each wanted object
    for wanted_object in wanted_objects:
        found = False

        # Iterate through the existing objects
        idx = 0
        while True:
            # Break out if nothing more to check
            if idx == len(existing_objects):
                break

            # If wanted object matches to an existing object, remove it from the list
            # and do not process it. It already exists -> nothing to do.
            existing_object = existing_objects[idx]

            if equal_fn(existing_object, wanted_object):
                found = True
                del existing_objects[idx]
            else:
                idx += 1

        # Wanted object not found -> we need to either find a new candidate for it or create it
        if not found:
            not_found.append(wanted_object)

    # Go through the wanted objects that did not match any existing objects
    for wanted_object in not_found:
        # Reuse one existing object that did not match any existing objects if there's still one available
        if existing_objects:
            existing = existing_objects.pop(0)

            # Overwrite the existing object
            save_fn(existing, wanted_object)
        else:
            create_fn(**wanted_object)

    # Finally, remove any old existing objects that did not match wanted object and did not get used
    if existing_objects:
        delete_fn(existing_objects)
