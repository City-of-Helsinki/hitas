from unittest.mock import MagicMock

from hitas.views.utils.merge import merge


class TestClass:
    def __init__(self, value, other_value):
        self.value = value
        self.other_value = other_value

        self.save = MagicMock()
        self.delete = MagicMock()


def eq(existing, wanted):
    return existing.value == wanted["value"] and existing.other_value == wanted["other_value"]


def test__merge__simple_add():
    create_fn = MagicMock()
    save_fn = MagicMock()
    delete_fn = MagicMock()

    # Setup
    wanted = {"value": 1, "other_value": 2}

    # Test
    merge([], [wanted], create_fn, lambda x, y: False, save_fn, delete_fn)

    # Validate new object was created
    create_fn.assert_called_once_with(**wanted)

    # Validate nothing else was done
    save_fn.assert_not_called()
    delete_fn.assert_not_called()


def test__merge__simple_remove():
    create_fn = MagicMock()
    save_fn = MagicMock()
    delete_fn = MagicMock()

    # Setup
    unwanted = MagicMock()

    # Test
    merge([unwanted], [], create_fn, lambda x, y: False, save_fn, delete_fn)

    # Validate delete_fn was called
    delete_fn.assert_called_once_with([unwanted])

    # Validate nothing was saved or created
    save_fn.assert_not_called()
    create_fn.assert_not_called()


def test__merge__simple_noop():
    create_fn = MagicMock()
    save_fn = MagicMock()
    delete_fn = MagicMock()

    # Setup
    wanted = {"value": 1, "other_value": 2}
    existing = MagicMock()

    # Test
    merge([existing], [wanted], create_fn, lambda x, y: True, save_fn, delete_fn)

    # Validate nothing was created, updated or deleted
    create_fn.assert_not_called()
    save_fn.assert_not_called()
    delete_fn.assert_not_called()


def test__merge__simple_update():
    create_fn = MagicMock()
    save_fn = MagicMock()
    delete_fn = MagicMock()

    # Setup
    wanted = MagicMock()
    existing = MagicMock()

    # Test
    merge([existing], [wanted], create_fn, lambda x, y: False, save_fn, delete_fn)

    # Validate existing object was reused
    save_fn.assert_called_once_with(existing, wanted)

    # Validate nothing was created or deleted
    create_fn.assert_not_called()
    delete_fn.assert_not_called()


def test__merge__complex_update__total_less():
    create_fn = MagicMock()
    save_fn = MagicMock()
    delete_fn = MagicMock()

    # Setup
    wanted1 = {"value": 44, "other_value": 44}  # New one, will replace `existing1`
    wanted2 = {"value": 3, "other_value": 3}  # Existing one, matches `existing3`

    existing1 = TestClass(value=1, other_value=1)
    existing2 = TestClass(value=2, other_value=2)
    existing3 = TestClass(value=3, other_value=3)

    # Test
    merge([existing1, existing2, existing3], [wanted1, wanted2], create_fn, eq, save_fn, delete_fn)

    # Validate

    # `existing1` was reused
    save_fn.assert_called_once_with(existing1, wanted1)

    # `existing2` was removed
    delete_fn.assert_called_once_with([existing2])

    # `existing3` was not modified

    # Nothing was created
    create_fn.assert_not_called()


def test__merge__complex_update__total_more():
    create_fn = MagicMock()
    save_fn = MagicMock()
    delete_fn = MagicMock()

    # Setup
    wanted1 = {"value": 11, "other_value": 11}  # New one, will replace `existing1`
    wanted2 = {"value": 2, "other_value": 2}  # Existing one, matches `existing2`
    wanted3 = {"value": 33, "other_value": 33}  # New one, will be created
    wanted4 = {"value": 3, "other_value": 3}  # Existing one, matches `existing3`

    existing1 = TestClass(value=1, other_value=1)
    existing2 = TestClass(value=2, other_value=2)
    existing3 = TestClass(value=3, other_value=3)

    # Test
    merge([existing1, existing2, existing3], [wanted1, wanted2, wanted3, wanted4], create_fn, eq, save_fn, delete_fn)

    # Validate

    # `existing1` was reused
    save_fn.assert_called_once_with(existing1, wanted1)

    # `existing2` was not modified in any way
    # `existing3` was not modified in any way

    # new object was created
    create_fn.assert_called_with(**wanted3)

    # delete was not called
    delete_fn.assert_not_called()
