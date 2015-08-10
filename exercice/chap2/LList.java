import java.lang.StringBuilder;

public class LList {
    Node head;
    int length = 0;

    public void add(int v) {
        this.length++;
        Node n = new Node(v);
        if (head == null) {
            // it is the first node
            head = n;
            return;
        }
        Node curr;
        for (curr = head; curr.next != null; curr = curr.next) {}
        // append n to tail
        curr.next = n;
    }
    
    public void add(int index, int v) {
        /*
        * three cases to consider:
        * 1. index < 0                  (error)
        * 2. index > list.length        (error)
        * 3. 0 <= index <= list.length  (normal)
        */
        Node n = new Node(v);
        if (index < 0) {
            // case 1: index < 0
            System.out.println("Error index! The index must no less than 0!");
            return;
        }
        Node curr = head;
        Node prev = null;
        for (int i = 0; i <= index; i++) {
            if (i == index) {
                // case 3: 0 <= index <= list.length
                this.length++;
                if(i == 0) {
                    n.next = head;
                    head   = n;
                    return;
                }
                prev.next = n;
                n.next    = curr;
                return;
            }
            if (curr.next == null && i+1 < index) {
                // case 2: index > list.length
                System.out.println("Error index! The index must no more than list length!");
                System.out.println("index = " + index + ". list length = " + (i+1));
                return;
            }
            prev = curr;
            curr = curr.next;
        }
    }

    public int get(int index) {
        if (index < 0 ) {
            // error case 1
            System.out.println("Error index! The index must no less than 0!");
            return -1;
        }
        if (index >= this.length) {
            // error case 2
            System.out.println("Error index! The index must less than list length!");
            System.out.println("index = " + index + ". list length = " + this.length);
            return -1;

        }
        if (index >= 0 && index < this.length) {
            Node curr = head;
            for (int i = 0; i < index; i++) {
                curr = curr.next;
            }
            return curr.value;
        }
        return -1;
    }

    public void delete(int index) {
        if (index < 0 ) {
            // error case 1
            System.out.println("Error index! The index must no less than 0!");
            return;
        }
        if (index >= this.length) {
            // error case 2
            System.out.println("Error index! The index must less than list length!");
            System.out.println("index = " + index + ". list length = " + this.length);
            return;

        }
        if (index >= 0 && index < this.length) {
            // normal case 3
            this.length--;
            if (index == 0) {
                head = head.next;
                return;
            }
            Node curr = head;
            Node prev = null; 
            for (int i = 0; i < index; i++) {
                prev = curr;
                curr = curr.next;
            }
            prev.next = curr.next;
            return;
        }
        return;
    }
    
    public LList get(int i1, int i2) {
        /*
        * return sub-linked-list from i1 to i2, inclusive
        */
        if (i1 < 0 || i2 > this.length) {
            System.out.println("Error index!");
            return null;
        }
        LList list = new LList();
        Node curr = head;
        for (int i = 0; i <= i2; i++) {
            if (i >= i1) {
                list.add(curr.value);
            }
            curr = curr.next;
        }
        return list;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (Node node = head; node != null; node = node.next) {
            sb.append(node.value);
        }
        return sb.toString();
    }


    public static void main(String[] args) {
        LList ll = new LList();
        ll.add(1);
        ll.add(2);
        ll.add(3);
        ll.add(0, 4);
        ll.add(1, 5);
        ll.add(4, 6);
        ll.add(6, 7);
        System.out.println(ll);
        System.out.println(ll.get(0));
        System.out.println(ll.get(3));
        System.out.println(ll.get(ll.length - 1));
        ll.delete(0);
        System.out.println(ll);
        ll.delete(3);
        System.out.println(ll);
        ll.delete(ll.length - 1);
        System.out.println(ll);
    }
}
