import java.util.HashSet;
import java.util.Iterator;

public class TestIterator {
    public static void main(String[] args) {
        HashSet<Integer> set = new HashSet<Integer>();
        set.add(1);
        set.add(2);
        set.add(3);
        Iterator<Integer> iter = set.iterator();
        System.out.println(iter);
        System.out.println(iter.next());
        System.out.println(iter.next());
        System.out.println(iter.next());
    }
}
