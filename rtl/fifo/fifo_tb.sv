// rtl/fifo/fifo_tb.sv - UPDATED
`timescale 1ns / 1ps

module fifo_tb;

  reg         clk;
  reg  [31:0] data_in;  // Changed from din to data_in
  wire [31:0] data_out;  // Changed from dout to data_out
  reg  [31:0] rdata;
  wire        empty;  // Now it's wire, not reg
  reg         rd_en;
  reg         wr_en;
  wire        full;
  reg         rst_n;  // Changed from rstn to rst_n
  reg         stop;

  // Instantiation with CORRECT names
  sync_fifo #(
      .DATA_WIDTH(32),
      .FIFO_DEPTH(16)
  ) u_sync_fifo (
      .rst_n   (rst_n),     // rst_n
      .wr_en   (wr_en),
      .rd_en   (rd_en),
      .clk     (clk),
      .data_in (data_in),   // data_in
      .data_out(data_out),  // data_out
      .empty   (empty),
      .full    (full)
  );

  // Clock generation: 50 MHz (20ns period)
  always #10 clk = ~clk;

  // Dump waveform
  initial begin
    $dumpfile("fifo.vcd");
    $dumpvars(0, fifo_tb);
  end

  initial begin
    clk = 0;
    rst_n = 0;
    wr_en = 0;
    rd_en = 0;
    stop = 0;
    data_in = 0;

    #50 rst_n = 1;
    $display("[%0t] Reset released", $time);
  end

  // Write process
  initial begin
    @(posedge rst_n);
    @(posedge clk);

    for (int i = 0; i < 20; i = i + 1) begin

      // Wait until there is space in fifo
      while (full) begin
        @(posedge clk);
        $display("[%0t] FIFO is full, waiting...", $time);
      end

      // Drive new values into FIFO
      wr_en   = $urandom_range(0, 1);  // Random write enable
      data_in = $urandom;  // Random data
      $display("[%0t] Write[%0d]: wr_en=%0d data_in=0x%08h", $time, i, wr_en, data_in);

      @(posedge clk);
      wr_en = 0;  // Disable write after one cycle
    end

    stop = 1;
    $display("[%0t] Write process finished", $time);
  end

  // Read process
  initial begin
    @(posedge rst_n);
    @(posedge clk);

    while (!stop) begin
      // Wait until there is data in fifo
      while (empty) begin
        rd_en = 0;
        $display("[%0t] FIFO is empty, waiting...", $time);
        @(posedge clk);
      end

      // Sample new values from FIFO
      rd_en = $urandom_range(0, 1);  // Random read enable
      @(posedge clk);
      rdata = data_out;
      $display("[%0t] Read: rd_en=%0d data_out=0x%08h", $time, rd_en, rdata);
      rd_en = 0;
    end

    #500;
    $display("[%0t] Simulation finished", $time);
    $finish;
  end

  // Timeout
  initial begin
    #10000;
    $display("[%0t] Timeout - simulation too long", $time);
    $finish;
  end

endmodule
