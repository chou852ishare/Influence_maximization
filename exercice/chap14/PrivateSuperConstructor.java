public class PrivateSuperConstructor extends Ex14_1 {
    
    public PrivateSuperConstructor() {
        super(2); 
        this.a = 0;
    }

    public static void main(String[] args) {
        PrivateSuperConstructor psc = new PrivateSuperConstructor();
        System.out.println(psc.getA());
    }
}
