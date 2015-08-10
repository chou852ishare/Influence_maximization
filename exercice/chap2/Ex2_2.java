public class Ex2_2 {
    public static void main(String[] args) {
        LList list = new LList();
        list.add(0);
        list.add(1);
        list.add(2);
        list.add(3);
        list.add(4);
        System.out.println("original list");
        System.out.println(list);
        int i1 = 3;
        int i2 = 4;
        System.out.println("sublist from " + i1 + " to " + i2);
        System.out.println(list.get(i1, i2));
    }
}
