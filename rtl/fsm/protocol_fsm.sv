`timescale 1ns / 1ps

module protocol_fsm (
    input  logic clk,
    input  logic rstn,
    input  logic in,
    output logic dout
);

  // State encoding
  typedef enum logic [1:0] {
    IDLE = 2'b00,
    SEND = 2'b01,
    WAIT = 2'b10,
    DONE = 2'b11
  } state_t;

  state_t cur_state, next_state;

  // State register
  always_ff @(posedge clk or negedge rstn) begin
    if (!rstn) cur_state <= IDLE;
    else cur_state <= next_state;
  end

  // Next-state logic
  always_comb begin
    next_state = cur_state;

    case (cur_state)
      IDLE: begin
        if (in) next_state = SEND;
      end

      SEND: begin
        next_state = WAIT;
      end

      WAIT: begin
        if (!in) next_state = DONE;
      end

      DONE: begin
        next_state = IDLE;
      end

      default: begin
        next_state = IDLE;
      end
    endcase
  end

  // Output logic (Moore)
  always_comb begin
    dout = 1'b0;

    case (cur_state)
      SEND: dout = 1'b1;
      default: dout = 1'b0;
    endcase
  end

endmodule
