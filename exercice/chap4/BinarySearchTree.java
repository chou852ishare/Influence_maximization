

public class BinarySearchTree {
    Node root;

    public void insert(int data) {
        if (root == null) {
            root = new Node(data);
            return;
        }
        insert(root, data);
    }

    private void insert(Node node, int data) {
        if (data <= node.data) {
            if (node.left == null) {
                node.left = new Node(data);
                return;
            }
            insert(node.left, data);
        } else {
            if (node.right == null) {
                node.right = new Node(data);
                return;
            }
            insert(node.right, data);
        }
    }

    public void inOrderTraversal() {
        System.out.println();
        System.out.println("root = " + root.data);
        inOrderHelper(root);
        System.out.println();
    }

    private void inOrderHelper(Node node) {
        if (node.left != null) 
            inOrderHelper(node.left);
        System.out.print(node.data + " ");
        if (node.right != null)
            inOrderHelper(node.right);
    }

    public void preOrderTraversal() {
        System.out.println();
        System.out.println("root = " + root.data);
        preOrderHelper(root);
        System.out.println();
    }
    
    public void preOrderHelper(Node node) {
        System.out.print(node.data + " ");
        if (node.left != null) 
            preOrderHelper(node.left);
        if (node.right != null) 
            preOrderHelper(node.right);
    }

    public void postOrderTraversal() {
        System.out.println();
        System.out.println("root = " + root.data);
        postOrderHelper(root);
        System.out.println();
    }
    
    public void postOrderHelper(Node node) {
        if (node.left != null) 
            postOrderHelper(node.left);
        if (node.right != null)
            postOrderHelper(node.right);
        System.out.print(node.data + " ");
    }

    public static void main(String[] args) {
        //int[] arr = {2, 1, 3, 8, 5, 4}; 
        //int[] arr = {1,5,2,7,4}; 
        //int[] arr = {11,8,6,4,7,10,19,43,31,29,37,49}; 
        int[] arr = {4,6,7,8,10,11,19,29,31,37,43,49};
        BinarySearchTree bst1 = new BinarySearchTree();
        BST              bst2 = new BST();
        for (int a : arr) {
            bst1.insert(a);
            bst2.insert(a);
        }
        bst1.inOrderTraversal();
        bst2.inOrderTraversal();
        bst1.preOrderTraversal();
        bst2.preOrderTraversal();
        bst1.postOrderTraversal();
    }
}
