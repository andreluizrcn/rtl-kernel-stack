`timescale 1ns / 1ps


module protocol_tb_fsm;

  logic clk;
  logic rstn;
  logic in;
  logic dout;

  protocol_fsm dut (
      .clk (clk),
      .rstn(rstn),
      .in  (in),
      .dout(dout)
  );

  initial clk = 0;
  always #5 clk = ~clk;


  // Dump waveform
  initial begin
    $dumpfile("fsm.vcd");
    $dumpvars(0, protocol_tb_fsm);
  end

  // Stimulus
  initial begin
    // Init
    rstn = 0;
    in   = 0;

    // Hold reset
    #20;
    rstn = 1;

    // IDLE → SEND
    #10;
    in = 1;

    // SEND → WAIT
    #20;

    // WAIT → DONE
    in = 0;
    #20;

    // DONE → IDLE
    #20;

    // Another round
    in = 1;
    #40;
    in = 0;
    #40;

    $finish;
  end


  initial begin
    $display(" time | rst in | dout ");
    $monitor("%4t |  %0b   %0b  |  %0b", $time, rstn, in, dout);
  end

endmodule
