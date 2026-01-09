module protocol_fsm (
    input  logic rstn,
    input  logic in,
    input  logic clk,
    output logic dout
);

  typedef enum logic [1:0] {
    IDLE,
    SEND,
    WAIT,
    DONE
  } state_t;

  state_t cur_state, next_state;


  //sequential block
  always_ff @(posedge clk) begin
    // If reset is asserted, go back to IDLE state
    if (!restn) begin
      cur_state <= IDLE;

      // Else transition to the next state
    end else begin
      cur_state <= next_state;
    end
  end


  // Combinational always block for next state logic
  always_comb @(*) begin
    // Default next state assignment
    next_state = IDLE;

    case (state)
      IDLE: begin
        if (input_signal) next_state = STATE_1;  // Transition to STATE_1 on input_signal
      end

      STATE_1: begin
        if (!input_signal) next_state = STATE_2;  // Transition to STATE_2 if input_signal is low
      end

      STATE_2: next_state = IDLE;  // Transition back to IDLE
      default: next_state = IDLE;  // Fallback to default state
    endcase
  end

  //output combinational block

  always_comb begin
    dout = 1'b0;

    case (cur_state)
      IDLE: dout = 1'b0;
      SEND: dout = 1'b1;
      WAIT: dout = 1'b0;
      DONE: dout = 1'b0;
      default: dout = 1'b0;
    endcase
  end

endmodule
