import java.util.LinkedList;
import java.util.Scanner;
import java.util.HashSet;

public class Ex2_1 {

    public void removeDuplicate(LinkedList<String> list) {
        /*
        * delete an element if duplicate
        */
        int ui;         // current index of unique list
        int ue = 1;     // end index of unique list, exclusive
        for (int oi = 1; oi < list.size(); oi++) {
            for (ui = 0; ui < ue; ui++) {
                // compare list[ui] with list[oi]
                if (list.get(ui).equals(list.get(oi))) {
                    list.remove(oi);
                    oi--;
                    break;
                }
            }
            if (ui == ue) {
                // meaning no duplicate element
                ue++;
            }
        }
    }
     
    public void makeSet(LinkedList<String> list) {
        HashSet<String> set = new HashSet<String>();
        for (int i = 0; i < list.size(); i++) {
            String s = list.get(i);
            if (!set.contains(s)) {
                set.add(s);
            } else {
                list.remove(i);
                i--;
            }
        }
    }

    public static void main(String[] args) {
        LinkedList<String> llist = new LinkedList<String>();
        Scanner scr = new Scanner(System.in);
        System.out.println("Please input some characters splited by space...");
        String line = scr.nextLine();
       
        // initialized llist
        String[] ss = line.split(" ");
        for (String s: ss) {
            llist.add(s);
        }
        System.out.print("original linked list");
        System.out.println(llist);
        
        // remove duplicate characters
        Ex2_1 ex21 = new Ex2_1();
        //ex21.removeDuplicate(llist);
        //System.out.print("unique linked list");
        //System.out.println(llist);
        ex21.makeSet(llist);
        System.out.print("set of linked list");
        System.out.println(llist);
    }
}
