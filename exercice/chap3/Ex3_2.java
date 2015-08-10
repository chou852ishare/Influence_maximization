import java.util.Stack;

public class Ex3_2 extends MyStack {
    Stack<SNode> minStack = new Stack<SNode>();
    
    @Override
    public void push(int value) {
        SNode node = new SNode(value);
        node.prev  = this.top;
        this.top   = node;
        // add node to minStack if it is current minimum
        if (minStack.empty()) {
            minStack.push(node);
            return;
        }
        if (minStack.peek().value >= value) {
            minStack.push(node);
            return;
        }
    }

    @Override 
    public int pop() {
        SNode node = this.top;
        this.top = this.top.prev;
        // update minStack if current minimum is popped out
        if (node.value == minStack.peek().value) {
            minStack.pop();
        }
        return node.value;
    }

    public int min() {
        return minStack.peek().value;
    }

    public static void main(String[] args) {
        Ex3_2 ex32 = new Ex3_2();
        ex32.push(3);
        ex32.push(2);
        ex32.push(8);
        ex32.push(0);
        ex32.push(0);
        ex32.push(2);
        ex32.push(2);
        ex32.push(8);
        ex32.push(0);
        System.out.println(ex32);
        System.out.println("min = " + ex32.min());
        ex32.pop();
        System.out.println(ex32);
        System.out.println("min = " + ex32.min());
        ex32.pop();
        System.out.println(ex32);
        System.out.println("min = " + ex32.min());
        ex32.pop();
        System.out.println(ex32);
        System.out.println("min = " + ex32.min());
        ex32.pop();
        System.out.println(ex32);
        System.out.println("min = " + ex32.min());
        ex32.pop();
        System.out.println(ex32);
        System.out.println("min = " + ex32.min());
        ex32.pop();
        System.out.println(ex32);
        System.out.println("min = " + ex32.min());
        ex32.pop();
        System.out.println(ex32);
        System.out.println("min = " + ex32.min());
    }
}
