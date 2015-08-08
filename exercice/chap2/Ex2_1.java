import java.util.LinkedList;

public class Ex2_1 {
    public static void main(String[] args) {
        LinkedList<Integer> llist = new LinkedList<Integer>();
        LList llist1 = new LList();
        llist.add(1);
        llist.add(2);
        llist.add(3);
        llist.add(1, 5);
        System.out.println(llist);
        System.out.println(llist1.head);
    }
}
