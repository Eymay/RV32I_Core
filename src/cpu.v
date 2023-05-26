
module cpu (clk,rst);

input wire clk;
input wire rst;

wire [31:0] r_for_pc;
wire [22:0] cword;
wire [31:0] inst;
wire [31:0] imm;
wire [31:0] pc;
wire [3:0] ZCNVFlags;


control_unit cu (
    .clk(clk),
    .rst(rst),
    .cword(cword),
    .pc(pc),
    .imm(imm),
    .inst(inst),
    .r_for_pc(r_for_pc),
    .ZCNVFlags(ZCNVFlags));
Datapath dp (
    .clk(clk),
    .rst(rst),
    .cword(cword),
    .pc(pc),
    .imm(imm),
    .r_for_pc(r_for_pc),
    .funit_ZCNVFlags(ZCNVFlags));
instr_mem instr_mem (
    .r_addr_imem(pc[6:0]), // TODO: this must be changed according to the inst mem size
    .r_data_imem(inst));

endmodule
