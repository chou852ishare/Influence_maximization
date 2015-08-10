import java.lang.StringBuilder;

public class MyStack {
    SNode top;

    public void push(int value) {
        /*
        * sNode(value).prev -> top, top -> SNode(value)
        * applies to first node
        */
        SNode node = new SNode(value);
        node.prev  = top;
        top        = node;
    }

    public int pop() {
        if (this.top != null) {
            int value = top.value;
            top = top.prev;
            return value;
        }
        System.out.println("Error! Stack is empty!");
        return -1;
    }
    
    public int peek() {
        if (this.top != null) {
            return top.value;
        }
        System.out.println("Error! Stack is empty!");
        return -1;
    }
    
    public boolean empty() {
        if (top == null) {
            return true;
        }
        return false;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (SNode n = this.top; n != null; n = n.prev) {
            sb.append(n.value);        
        }
        return sb.reverse().toString();
    }

    public static void main(String[] args) {
        MyStack stack = new MyStack();
        stack.push(1);
        stack.push(2);
        stack.push(4);
        System.out.println(stack);
        stack.pop();
        stack.pop();
        System.out.println(stack);
    }
}
