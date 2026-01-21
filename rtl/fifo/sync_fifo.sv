// rtl/fifo/fifo.sv
module sync_fifo #(
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 4,   // Depth = 2^ADDR_WIDTH
    parameter FIFO_DEPTH = 16
) (
    input wire clk,
    input wire rst_n,

    // Write interface
    input wire wr_en,
    input wire [DATA_WIDTH-1:0] data_in,
    output wire full,

    // Read interface
    input wire rd_en,
    output wire [DATA_WIDTH-1:0] data_out,
    output wire empty
);

  // Internal memory
  reg [DATA_WIDTH-1:0] mem[0:FIFO_DEPTH-1];

  // Pointers
  reg [ADDR_WIDTH:0] wr_ptr = 0;  // MSB for full/empty detection
  reg [ADDR_WIDTH:0] rd_ptr = 0;

  // Status flags
  wire [ADDR_WIDTH:0] wr_ptr_gray;
  wire [ADDR_WIDTH:0] rd_ptr_gray;

  // Empty when pointers are equal
  assign empty = (wr_ptr == rd_ptr);

  // Full when pointers differ by FIFO_DEPTH
  assign full = ((wr_ptr[ADDR_WIDTH-1:0] == rd_ptr[ADDR_WIDTH-1:0]) &&
                   (wr_ptr[ADDR_WIDTH] != rd_ptr[ADDR_WIDTH]));

  // Data output
  assign data_out = mem[rd_ptr[ADDR_WIDTH-1:0]];

  // Write operation
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      wr_ptr <= 0;
    end else if (wr_en && !full) begin
      mem[wr_ptr[ADDR_WIDTH-1:0]] <= data_in;
      wr_ptr <= wr_ptr + 1;
    end
  end

  // Read operation
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      rd_ptr <= 0;
    end else if (rd_en && !empty) begin
      rd_ptr <= rd_ptr + 1;
    end
  end

  // Gray code conversion (for clock domain crossing if async)
  function [ADDR_WIDTH:0] binary_to_gray(input [ADDR_WIDTH:0] bin);
    binary_to_gray = bin ^ (bin >> 1);
  endfunction

  assign wr_ptr_gray = binary_to_gray(wr_ptr);
  assign rd_ptr_gray = binary_to_gray(rd_ptr);

endmodule
