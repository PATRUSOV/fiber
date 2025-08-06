from fiber.pipeline.task.utils.datastructs import get_linked_list_from, Node


def test_getting_linked_list():
    objects = [object(), object(), object()]

    head_node = get_linked_list_from(objects)

    node = head_node
    for obj in objects:
        assert node is not None

        assert node.item is obj
        node = node.next

    assert node is None


def testing_node_state_state():
    item = object()
    node = Node(item)

    assert node.item is item
    assert node.next is None
