module instr_mem(
    input [6:0] r_addr_imem,
    output reg [31:0] r_data_imem
);

reg [7:0] imem [127:0];
//param_mux #(.input_length(32), .X_to_1(32)) mux(.i_mux(imem), .select(r_addr_imem), .o_mux(r_data_imem));
initial $readmemh("C:/Users/Can/Documents/hw_projects/hw9/test.mem", imem);
 
always @(*) begin
    r_data_imem = {imem[r_addr_imem + 3],imem[r_addr_imem + 2],imem[r_addr_imem + 1],imem[r_addr_imem]};    
end
endmodule