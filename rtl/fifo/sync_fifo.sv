module sync_fifo #(
    parameter int DEPTH  = 8,
    parameter int DWIDTH = 16
) (
    input  logic              rstn,   // Active low reset
    input  logic              clk,    // Clock
    input  logic              wr_en,  // Write enable
    input  logic              rd_en,  // Read enable
    input  logic [DWIDTH-1:0] din,    // Data written into FIFO
    output logic [DWIDTH-1:0] dout,   // Data read from FIFO
    output logic              empty,  // FIFO is empty when high
    output logic              full    // FIFO is full when high
);

  //write side
  logic [$clog2(DEPTH)-1:0] wptr, rptr;
  logic [DWIDTH-1:0] fifo[DEPTH];  // width x depth = mem size

  always_ff @(posedge clk or negedge rstn) begin
    if (!rstn) begin
      wptr <= '0;
    end else begin
      if (wr_en & !full) begin
        fifo[wptr] <= din;
        wptr <= wptr + 1;
      end
    end
  end

  initial begin
    $monitor("[%0t] [FIFO] wr_en=%0b din=0x%0h rd_en=%0b dout=0x%0h empty=%0b full=%0b", $time,
             wr_en, din, rd_en, dout, empty, full);
  end

  //read side
  always_ff @(posedge clk or negedge rstn) begin
    if (!rstn) begin
      rptr <= '0;
    end else begin
      if (rd_en & !empty) begin
        dout <= fifo[rptr];
        rptr <= rptr + 1;
      end
    end
  end

  always_comb begin
    full  = (wptr + 1) == rptr;
    empty = wptr == rptr;
  end

endmodule
