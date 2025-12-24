//#TODO: define parameter DEPTH=8, DWIDTH=16

module fifo (
    input                   rstn,  // Active low reset
    clk,  // Clock
    wr_en,  // Write enable
    rd_en,  // Read enable
    input      [DWIDTH-1:0] din,   // Data written into FIFO
    output reg [DWIDTH-1:0] dout,  // Data read from FIFO
    output                  empty, // FIFO is empty when high
    full  // FIFO is full when high
);

  //#TODO: write the content here



  assign full  = (wptr + 1) == rptr;
  assign empty = wptr == rptr;
endmodule
