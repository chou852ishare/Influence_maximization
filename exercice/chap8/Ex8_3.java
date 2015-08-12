import java.util.Scanner;
import java.util.HashSet;
import java.util.ArrayList;
import java.util.Iterator;

public class Ex8_3 {
    
    public ArrayList<String> enumSubsets(HashSet<Integer> set) {
        ArrayList<String> subsets = new ArrayList<String>();
        Iterator<Integer> iter = set.iterator();
        if (iter.hasNext()) {
            Integer i = iter.next();
            set.remove(i);
            for (String s : enumSubsets(set)) {
                subsets.add(s);
                subsets.add(i + s);
            }
            return subsets;
        } else {
            subsets.add("");
            return subsets;
        }
    }

    public static void main(String[] args) {
        System.out.println("please input numbers...");
        Scanner scan = new Scanner(System.in);
        String[] ss  = scan.nextLine().split(" ");
        HashSet<Integer> set = new HashSet<Integer>();
        for (String s : ss) 
            set.add(Integer.parseInt(s));
        
        Ex8_3 ex83 = new Ex8_3();
        for (String s : ex83.enumSubsets(set)) {
            System.out.println(s);
        }
    }
}
