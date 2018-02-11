# Generated from Lua.g4 by ANTLR 4.7
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .LuaParser import LuaParser
else:
    from LuaParser import LuaParser

# This class defines a complete listener for a parse tree produced by LuaParser.
class LuaListener(ParseTreeListener):

    # Enter a parse tree produced by LuaParser#chunk.
    def enterChunk(self, ctx:LuaParser.ChunkContext):
        pass

    # Exit a parse tree produced by LuaParser#chunk.
    def exitChunk(self, ctx:LuaParser.ChunkContext):
        pass


    # Enter a parse tree produced by LuaParser#block.
    def enterBlock(self, ctx:LuaParser.BlockContext):
        pass

    # Exit a parse tree produced by LuaParser#block.
    def exitBlock(self, ctx:LuaParser.BlockContext):
        pass


    # Enter a parse tree produced by LuaParser#stat.
    def enterStat(self, ctx:LuaParser.StatContext):
        pass

    # Exit a parse tree produced by LuaParser#stat.
    def exitStat(self, ctx:LuaParser.StatContext):
        pass


    # Enter a parse tree produced by LuaParser#do_block.
    def enterDo_block(self, ctx:LuaParser.Do_blockContext):
        pass

    # Exit a parse tree produced by LuaParser#do_block.
    def exitDo_block(self, ctx:LuaParser.Do_blockContext):
        pass


    # Enter a parse tree produced by LuaParser#while_stat.
    def enterWhile_stat(self, ctx:LuaParser.While_statContext):
        pass

    # Exit a parse tree produced by LuaParser#while_stat.
    def exitWhile_stat(self, ctx:LuaParser.While_statContext):
        pass


    # Enter a parse tree produced by LuaParser#repeat_stat.
    def enterRepeat_stat(self, ctx:LuaParser.Repeat_statContext):
        pass

    # Exit a parse tree produced by LuaParser#repeat_stat.
    def exitRepeat_stat(self, ctx:LuaParser.Repeat_statContext):
        pass


    # Enter a parse tree produced by LuaParser#assignment.
    def enterAssignment(self, ctx:LuaParser.AssignmentContext):
        pass

    # Exit a parse tree produced by LuaParser#assignment.
    def exitAssignment(self, ctx:LuaParser.AssignmentContext):
        pass


    # Enter a parse tree produced by LuaParser#local.
    def enterLocal(self, ctx:LuaParser.LocalContext):
        pass

    # Exit a parse tree produced by LuaParser#local.
    def exitLocal(self, ctx:LuaParser.LocalContext):
        pass


    # Enter a parse tree produced by LuaParser#goto_stat.
    def enterGoto_stat(self, ctx:LuaParser.Goto_statContext):
        pass

    # Exit a parse tree produced by LuaParser#goto_stat.
    def exitGoto_stat(self, ctx:LuaParser.Goto_statContext):
        pass


    # Enter a parse tree produced by LuaParser#if_stat.
    def enterIf_stat(self, ctx:LuaParser.If_statContext):
        pass

    # Exit a parse tree produced by LuaParser#if_stat.
    def exitIf_stat(self, ctx:LuaParser.If_statContext):
        pass


    # Enter a parse tree produced by LuaParser#elseif_stat.
    def enterElseif_stat(self, ctx:LuaParser.Elseif_statContext):
        pass

    # Exit a parse tree produced by LuaParser#elseif_stat.
    def exitElseif_stat(self, ctx:LuaParser.Elseif_statContext):
        pass


    # Enter a parse tree produced by LuaParser#else_stat.
    def enterElse_stat(self, ctx:LuaParser.Else_statContext):
        pass

    # Exit a parse tree produced by LuaParser#else_stat.
    def exitElse_stat(self, ctx:LuaParser.Else_statContext):
        pass


    # Enter a parse tree produced by LuaParser#for_stat.
    def enterFor_stat(self, ctx:LuaParser.For_statContext):
        pass

    # Exit a parse tree produced by LuaParser#for_stat.
    def exitFor_stat(self, ctx:LuaParser.For_statContext):
        pass


    # Enter a parse tree produced by LuaParser#function.
    def enterFunction(self, ctx:LuaParser.FunctionContext):
        pass

    # Exit a parse tree produced by LuaParser#function.
    def exitFunction(self, ctx:LuaParser.FunctionContext):
        pass


    # Enter a parse tree produced by LuaParser#names.
    def enterNames(self, ctx:LuaParser.NamesContext):
        pass

    # Exit a parse tree produced by LuaParser#names.
    def exitNames(self, ctx:LuaParser.NamesContext):
        pass


    # Enter a parse tree produced by LuaParser#function_literal.
    def enterFunction_literal(self, ctx:LuaParser.Function_literalContext):
        pass

    # Exit a parse tree produced by LuaParser#function_literal.
    def exitFunction_literal(self, ctx:LuaParser.Function_literalContext):
        pass


    # Enter a parse tree produced by LuaParser#func_body.
    def enterFunc_body(self, ctx:LuaParser.Func_bodyContext):
        pass

    # Exit a parse tree produced by LuaParser#func_body.
    def exitFunc_body(self, ctx:LuaParser.Func_bodyContext):
        pass


    # Enter a parse tree produced by LuaParser#param_list.
    def enterParam_list(self, ctx:LuaParser.Param_listContext):
        pass

    # Exit a parse tree produced by LuaParser#param_list.
    def exitParam_list(self, ctx:LuaParser.Param_listContext):
        pass


    # Enter a parse tree produced by LuaParser#ret_stat.
    def enterRet_stat(self, ctx:LuaParser.Ret_statContext):
        pass

    # Exit a parse tree produced by LuaParser#ret_stat.
    def exitRet_stat(self, ctx:LuaParser.Ret_statContext):
        pass


    # Enter a parse tree produced by LuaParser#expr.
    def enterExpr(self, ctx:LuaParser.ExprContext):
        pass

    # Exit a parse tree produced by LuaParser#expr.
    def exitExpr(self, ctx:LuaParser.ExprContext):
        pass


    # Enter a parse tree produced by LuaParser#or_expr.
    def enterOr_expr(self, ctx:LuaParser.Or_exprContext):
        pass

    # Exit a parse tree produced by LuaParser#or_expr.
    def exitOr_expr(self, ctx:LuaParser.Or_exprContext):
        pass


    # Enter a parse tree produced by LuaParser#and_expr.
    def enterAnd_expr(self, ctx:LuaParser.And_exprContext):
        pass

    # Exit a parse tree produced by LuaParser#and_expr.
    def exitAnd_expr(self, ctx:LuaParser.And_exprContext):
        pass


    # Enter a parse tree produced by LuaParser#rel_expr.
    def enterRel_expr(self, ctx:LuaParser.Rel_exprContext):
        pass

    # Exit a parse tree produced by LuaParser#rel_expr.
    def exitRel_expr(self, ctx:LuaParser.Rel_exprContext):
        pass


    # Enter a parse tree produced by LuaParser#concat_expr.
    def enterConcat_expr(self, ctx:LuaParser.Concat_exprContext):
        pass

    # Exit a parse tree produced by LuaParser#concat_expr.
    def exitConcat_expr(self, ctx:LuaParser.Concat_exprContext):
        pass


    # Enter a parse tree produced by LuaParser#add_expr.
    def enterAdd_expr(self, ctx:LuaParser.Add_exprContext):
        pass

    # Exit a parse tree produced by LuaParser#add_expr.
    def exitAdd_expr(self, ctx:LuaParser.Add_exprContext):
        pass


    # Enter a parse tree produced by LuaParser#mult_expr.
    def enterMult_expr(self, ctx:LuaParser.Mult_exprContext):
        pass

    # Exit a parse tree produced by LuaParser#mult_expr.
    def exitMult_expr(self, ctx:LuaParser.Mult_exprContext):
        pass


    # Enter a parse tree produced by LuaParser#bitwise_expr.
    def enterBitwise_expr(self, ctx:LuaParser.Bitwise_exprContext):
        pass

    # Exit a parse tree produced by LuaParser#bitwise_expr.
    def exitBitwise_expr(self, ctx:LuaParser.Bitwise_exprContext):
        pass


    # Enter a parse tree produced by LuaParser#unary_expr.
    def enterUnary_expr(self, ctx:LuaParser.Unary_exprContext):
        pass

    # Exit a parse tree produced by LuaParser#unary_expr.
    def exitUnary_expr(self, ctx:LuaParser.Unary_exprContext):
        pass


    # Enter a parse tree produced by LuaParser#pow_expr.
    def enterPow_expr(self, ctx:LuaParser.Pow_exprContext):
        pass

    # Exit a parse tree produced by LuaParser#pow_expr.
    def exitPow_expr(self, ctx:LuaParser.Pow_exprContext):
        pass


    # Enter a parse tree produced by LuaParser#atom.
    def enterAtom(self, ctx:LuaParser.AtomContext):
        pass

    # Exit a parse tree produced by LuaParser#atom.
    def exitAtom(self, ctx:LuaParser.AtomContext):
        pass


    # Enter a parse tree produced by LuaParser#var.
    def enterVar(self, ctx:LuaParser.VarContext):
        pass

    # Exit a parse tree produced by LuaParser#var.
    def exitVar(self, ctx:LuaParser.VarContext):
        pass


    # Enter a parse tree produced by LuaParser#callee.
    def enterCallee(self, ctx:LuaParser.CalleeContext):
        pass

    # Exit a parse tree produced by LuaParser#callee.
    def exitCallee(self, ctx:LuaParser.CalleeContext):
        pass


    # Enter a parse tree produced by LuaParser#tail_dot_index.
    def enterTail_dot_index(self, ctx:LuaParser.Tail_dot_indexContext):
        pass

    # Exit a parse tree produced by LuaParser#tail_dot_index.
    def exitTail_dot_index(self, ctx:LuaParser.Tail_dot_indexContext):
        pass


    # Enter a parse tree produced by LuaParser#tail_brack_index.
    def enterTail_brack_index(self, ctx:LuaParser.Tail_brack_indexContext):
        pass

    # Exit a parse tree produced by LuaParser#tail_brack_index.
    def exitTail_brack_index(self, ctx:LuaParser.Tail_brack_indexContext):
        pass


    # Enter a parse tree produced by LuaParser#tail_invoke.
    def enterTail_invoke(self, ctx:LuaParser.Tail_invokeContext):
        pass

    # Exit a parse tree produced by LuaParser#tail_invoke.
    def exitTail_invoke(self, ctx:LuaParser.Tail_invokeContext):
        pass


    # Enter a parse tree produced by LuaParser#tail_invoke_table.
    def enterTail_invoke_table(self, ctx:LuaParser.Tail_invoke_tableContext):
        pass

    # Exit a parse tree produced by LuaParser#tail_invoke_table.
    def exitTail_invoke_table(self, ctx:LuaParser.Tail_invoke_tableContext):
        pass


    # Enter a parse tree produced by LuaParser#tail_invoke_str.
    def enterTail_invoke_str(self, ctx:LuaParser.Tail_invoke_strContext):
        pass

    # Exit a parse tree produced by LuaParser#tail_invoke_str.
    def exitTail_invoke_str(self, ctx:LuaParser.Tail_invoke_strContext):
        pass


    # Enter a parse tree produced by LuaParser#tail_call.
    def enterTail_call(self, ctx:LuaParser.Tail_callContext):
        pass

    # Exit a parse tree produced by LuaParser#tail_call.
    def exitTail_call(self, ctx:LuaParser.Tail_callContext):
        pass


    # Enter a parse tree produced by LuaParser#tail_table.
    def enterTail_table(self, ctx:LuaParser.Tail_tableContext):
        pass

    # Exit a parse tree produced by LuaParser#tail_table.
    def exitTail_table(self, ctx:LuaParser.Tail_tableContext):
        pass


    # Enter a parse tree produced by LuaParser#tail_string.
    def enterTail_string(self, ctx:LuaParser.Tail_stringContext):
        pass

    # Exit a parse tree produced by LuaParser#tail_string.
    def exitTail_string(self, ctx:LuaParser.Tail_stringContext):
        pass


    # Enter a parse tree produced by LuaParser#table_constructor.
    def enterTable_constructor(self, ctx:LuaParser.Table_constructorContext):
        pass

    # Exit a parse tree produced by LuaParser#table_constructor.
    def exitTable_constructor(self, ctx:LuaParser.Table_constructorContext):
        pass


    # Enter a parse tree produced by LuaParser#field_list.
    def enterField_list(self, ctx:LuaParser.Field_listContext):
        pass

    # Exit a parse tree produced by LuaParser#field_list.
    def exitField_list(self, ctx:LuaParser.Field_listContext):
        pass


    # Enter a parse tree produced by LuaParser#field.
    def enterField(self, ctx:LuaParser.FieldContext):
        pass

    # Exit a parse tree produced by LuaParser#field.
    def exitField(self, ctx:LuaParser.FieldContext):
        pass


    # Enter a parse tree produced by LuaParser#field_sep.
    def enterField_sep(self, ctx:LuaParser.Field_sepContext):
        pass

    # Exit a parse tree produced by LuaParser#field_sep.
    def exitField_sep(self, ctx:LuaParser.Field_sepContext):
        pass


    # Enter a parse tree produced by LuaParser#label.
    def enterLabel(self, ctx:LuaParser.LabelContext):
        pass

    # Exit a parse tree produced by LuaParser#label.
    def exitLabel(self, ctx:LuaParser.LabelContext):
        pass


    # Enter a parse tree produced by LuaParser#var_list.
    def enterVar_list(self, ctx:LuaParser.Var_listContext):
        pass

    # Exit a parse tree produced by LuaParser#var_list.
    def exitVar_list(self, ctx:LuaParser.Var_listContext):
        pass


    # Enter a parse tree produced by LuaParser#expr_list.
    def enterExpr_list(self, ctx:LuaParser.Expr_listContext):
        pass

    # Exit a parse tree produced by LuaParser#expr_list.
    def exitExpr_list(self, ctx:LuaParser.Expr_listContext):
        pass


    # Enter a parse tree produced by LuaParser#name_list.
    def enterName_list(self, ctx:LuaParser.Name_listContext):
        pass

    # Exit a parse tree produced by LuaParser#name_list.
    def exitName_list(self, ctx:LuaParser.Name_listContext):
        pass


