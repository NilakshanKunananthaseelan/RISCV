`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/24/2017 06:54:42 PM
// Design Name: 
// Module Name: IMM_EXT
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module IMM_EXT(
    input       [31:7]   INS     ,
    input       [2:0]    TYPE    ,
    output      [31:0]  OUTPUT
    );
    reg [31:0] imm_out [7:0]  ;
    
    `include "PipelineParams.vh"
    
    always @(*)
    begin
       imm_out [ itype]= {{21{INS[31]}},INS[30:20]};
       imm_out [ stype]= {{21{INS[31]}},INS[30:25],INS[11:7]};
       imm_out [ btype]= {{20{INS[31]}},INS[7],INS[30:25],INS[11:8],1'b0}; 
       imm_out [ utype]= {INS[31:12],12'd0};
       imm_out [ jtype]={{12{INS[31]}},INS[19:12],INS[20],INS[30:25],INS[24:21],1'b0};
       imm_out [ ntype]= 32'd0;  
       imm_out [ rtype]= 32'd0;
    end
    Multiplexer #(
                                   .ORDER(3),
                                   .WIDTH(32)
                               ) 
        imm_mux (
                                   .SELECT(TYPE),
                                   .IN(
                                       {
                                       32'd0,
                                       imm_out[6],
                                       imm_out[5],
                                       imm_out[4],
                                       imm_out[3],
                                       imm_out[2],
                                       imm_out[1],
                                       imm_out[0]
                                       
                                       }),
                                    .OUT(OUTPUT)
                                    );
endmodule
