
class NameHasher:
    def __init__(self):
        self.char_map = self._build_char_map()

    def _build_char_map(self):
        ukr_letters = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
        char_map = {}
        for i, c in enumerate(ukr_letters):
            char_map[c] = i + 1
        return char_map

    def hash_name(self, name: str) -> int:
        name = name.upper()
        base = 100
        max_chars = 3
        hash_val = 0

        for i in range(max_chars):
            hash_val *= base
            if i < len(name):
                hash_val += self.char_map.get(name[i], 0)
            else:
                hash_val += 0

        hash_val = hash_val * 10 + min(len(name), 9)
        return hash_val

class BPlusTreeNode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.next = None


class BPlusTree:
    def __init__(self, order=4):
        self.root = BPlusTreeNode(is_leaf=True)
        self.order = order

    def find_leaf(self, key):
        current = self.root
        while not current.is_leaf:
            i = 0
            while i < len(current.keys) and key >= current.keys[i]:
                i += 1
            current = current.children[i]
        return current

    def insert(self, key, value):
        leaf = self.find_leaf(key)
        insert_index = 0
        while insert_index < len(leaf.keys) and key > leaf.keys[insert_index]:
            insert_index += 1
        leaf.keys.insert(insert_index, key)
        leaf.children.insert(insert_index, value)

        if len(leaf.keys) > self.order - 1:
            self.split(leaf)

    def split(self, node):
        mid_index = len(node.keys) // 2
        new_node = BPlusTreeNode(is_leaf=node.is_leaf)

        new_node.keys = node.keys[mid_index:]
        new_node.children = node.children[mid_index:]
        node.keys = node.keys[:mid_index]
        node.children = node.children[:mid_index]

        if node.is_leaf:
            new_node.next = node.next
            node.next = new_node

        if node == self.root:
            new_root = BPlusTreeNode()
            new_root.keys = [new_node.keys[0]]
            new_root.children = [node, new_node]
            self.root = new_root
        else:
            parent = self.find_parent(self.root, node)
            if parent is not None:
                insert_index = parent.children.index(node) + 1
                parent.keys.insert(insert_index - 1, new_node.keys[0])
                parent.children.insert(insert_index, new_node)
                if len(parent.keys) > self.order - 1:
                    self.split(parent)

    def find_parent(self, current, child):
        if current.is_leaf or current.children[0].is_leaf:
            return None
        for i in range(len(current.children)):
            if current.children[i] == child:
                return current
            else:
                res = self.find_parent(current.children[i], child)
                if res:
                    return res
        return None

    def search(self, key):
        leaf = self.find_leaf(key)
        for i, k in enumerate(leaf.keys):
            if k == key:
                return [leaf.children[i]]
        return None

    def search_greater(self, key):
        result = []
        leaf = self.find_leaf(key)
        while leaf:
            for k, v in zip(leaf.keys, leaf.children):
                if k > key:
                    result.append((k, v))
            leaf = leaf.next
        return [v for k, v in sorted(result)]

    def search_less(self, key):
        result = []
        current = self.root
        while not current.is_leaf:
            current = current.children[0]
        while current:
            for k, v in zip(current.keys, current.children):
                if k < key:
                    result.append((k, v))
            current = current.next
        return [v for k, v in sorted(result)]
    def delete(self, key):
        leaf = self.find_leaf(key)
        if key not in leaf.keys:
            return False

        index = leaf.keys.index(key)
        del leaf.keys[index]
        del leaf.children[index]

        if self.root == leaf and len(leaf.keys) == 0:
            self.root = BPlusTreeNode(is_leaf=True)
            return True

        min_keys = (self.order + 1) // 2 - 1

        if len(leaf.keys) < min_keys:
            self._rebalance_after_delete(leaf)

        return True

    def _rebalance_after_delete(self, node):
        parent = self.find_parent(self.root, node)
        if not parent:
            return

        index = parent.children.index(node)

        left_sibling = parent.children[index - 1] if index > 0 else None
        right_sibling = parent.children[index + 1] if index + 1 < len(parent.children) else None

        min_keys = (self.order + 1) // 2 - 1

        if left_sibling and len(left_sibling.keys) > min_keys:
            borrowed_key = left_sibling.keys.pop(-1)
            borrowed_val = left_sibling.children.pop(-1)
            node.keys.insert(0, borrowed_key)
            node.children.insert(0, borrowed_val)
            parent.keys[index - 1] = node.keys[0]
            return

        if right_sibling and len(right_sibling.keys) > min_keys:
            borrowed_key = right_sibling.keys.pop(0)
            borrowed_val = right_sibling.children.pop(0)
            node.keys.append(borrowed_key)
            node.children.append(borrowed_val)
            parent.keys[index] = right_sibling.keys[0]
            return

        if left_sibling:
            left_sibling.keys.extend(node.keys)
            left_sibling.children.extend(node.children)
            left_sibling.next = node.next
            del parent.keys[index - 1]
            del parent.children[index]
        elif right_sibling:
            node.keys.extend(right_sibling.keys)
            node.children.extend(right_sibling.children)
            node.next = right_sibling.next
            del parent.keys[index]
            del parent.children[index + 1]

        if parent == self.root and len(parent.keys) == 0:
            self.root = parent.children[0]
        elif len(parent.keys) < (self.order + 1) // 2 - 1:
            self._rebalance_after_delete(parent)





hasher = NameHasher()
tree = BPlusTree(order=4)

names = ["Зайченко", "Заєць", "Курча", "Андрій", "Іван", "Ігор", "Оксана"]
for name in names:
    h = hasher.hash_name(name)
    tree.insert(h, name)

print("пошук Заєць:", tree.search(hasher.hash_name("Заєць")))
print("іімена більше Заєць:", tree.search_greater(hasher.hash_name("Заєць")))
print("імена менше Заєць:", tree.search_less(hasher.hash_name("Заєць")))
print("до видалення Іван:", tree.search(hasher.hash_name("Іван")))
tree.delete(hasher.hash_name("Іван"))
print("після видалення іван:", tree.search(hasher.hash_name("Іван")))
print("імена більше іван:", tree.search_greater(hasher.hash_name("Іван")))

