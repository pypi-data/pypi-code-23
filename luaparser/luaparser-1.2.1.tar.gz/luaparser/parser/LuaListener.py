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


    # Enter a parse tree produced by LuaParser#setStat.
    def enterSetStat(self, ctx:LuaParser.SetStatContext):
        pass

    # Exit a parse tree produced by LuaParser#setStat.
    def exitSetStat(self, ctx:LuaParser.SetStatContext):
        pass


    # Enter a parse tree produced by LuaParser#call.
    def enterCall(self, ctx:LuaParser.CallContext):
        pass

    # Exit a parse tree produced by LuaParser#call.
    def exitCall(self, ctx:LuaParser.CallContext):
        pass


    # Enter a parse tree produced by LuaParser#invoke.
    def enterInvoke(self, ctx:LuaParser.InvokeContext):
        pass

    # Exit a parse tree produced by LuaParser#invoke.
    def exitInvoke(self, ctx:LuaParser.InvokeContext):
        pass


    # Enter a parse tree produced by LuaParser#label.
    def enterLabel(self, ctx:LuaParser.LabelContext):
        pass

    # Exit a parse tree produced by LuaParser#label.
    def exitLabel(self, ctx:LuaParser.LabelContext):
        pass


    # Enter a parse tree produced by LuaParser#breakStat.
    def enterBreakStat(self, ctx:LuaParser.BreakStatContext):
        pass

    # Exit a parse tree produced by LuaParser#breakStat.
    def exitBreakStat(self, ctx:LuaParser.BreakStatContext):
        pass


    # Enter a parse tree produced by LuaParser#goto.
    def enterGoto(self, ctx:LuaParser.GotoContext):
        pass

    # Exit a parse tree produced by LuaParser#goto.
    def exitGoto(self, ctx:LuaParser.GotoContext):
        pass


    # Enter a parse tree produced by LuaParser#do.
    def enterDo(self, ctx:LuaParser.DoContext):
        pass

    # Exit a parse tree produced by LuaParser#do.
    def exitDo(self, ctx:LuaParser.DoContext):
        pass


    # Enter a parse tree produced by LuaParser#whileStat.
    def enterWhileStat(self, ctx:LuaParser.WhileStatContext):
        pass

    # Exit a parse tree produced by LuaParser#whileStat.
    def exitWhileStat(self, ctx:LuaParser.WhileStatContext):
        pass


    # Enter a parse tree produced by LuaParser#repeat.
    def enterRepeat(self, ctx:LuaParser.RepeatContext):
        pass

    # Exit a parse tree produced by LuaParser#repeat.
    def exitRepeat(self, ctx:LuaParser.RepeatContext):
        pass


    # Enter a parse tree produced by LuaParser#ifStat.
    def enterIfStat(self, ctx:LuaParser.IfStatContext):
        pass

    # Exit a parse tree produced by LuaParser#ifStat.
    def exitIfStat(self, ctx:LuaParser.IfStatContext):
        pass


    # Enter a parse tree produced by LuaParser#fornum.
    def enterFornum(self, ctx:LuaParser.FornumContext):
        pass

    # Exit a parse tree produced by LuaParser#fornum.
    def exitFornum(self, ctx:LuaParser.FornumContext):
        pass


    # Enter a parse tree produced by LuaParser#forin.
    def enterForin(self, ctx:LuaParser.ForinContext):
        pass

    # Exit a parse tree produced by LuaParser#forin.
    def exitForin(self, ctx:LuaParser.ForinContext):
        pass


    # Enter a parse tree produced by LuaParser#func.
    def enterFunc(self, ctx:LuaParser.FuncContext):
        pass

    # Exit a parse tree produced by LuaParser#func.
    def exitFunc(self, ctx:LuaParser.FuncContext):
        pass


    # Enter a parse tree produced by LuaParser#localfunc.
    def enterLocalfunc(self, ctx:LuaParser.LocalfuncContext):
        pass

    # Exit a parse tree produced by LuaParser#localfunc.
    def exitLocalfunc(self, ctx:LuaParser.LocalfuncContext):
        pass


    # Enter a parse tree produced by LuaParser#localset.
    def enterLocalset(self, ctx:LuaParser.LocalsetContext):
        pass

    # Exit a parse tree produced by LuaParser#localset.
    def exitLocalset(self, ctx:LuaParser.LocalsetContext):
        pass


    # Enter a parse tree produced by LuaParser#elseIfStat.
    def enterElseIfStat(self, ctx:LuaParser.ElseIfStatContext):
        pass

    # Exit a parse tree produced by LuaParser#elseIfStat.
    def exitElseIfStat(self, ctx:LuaParser.ElseIfStatContext):
        pass


    # Enter a parse tree produced by LuaParser#elseStat.
    def enterElseStat(self, ctx:LuaParser.ElseStatContext):
        pass

    # Exit a parse tree produced by LuaParser#elseStat.
    def exitElseStat(self, ctx:LuaParser.ElseStatContext):
        pass


    # Enter a parse tree produced by LuaParser#retstat.
    def enterRetstat(self, ctx:LuaParser.RetstatContext):
        pass

    # Exit a parse tree produced by LuaParser#retstat.
    def exitRetstat(self, ctx:LuaParser.RetstatContext):
        pass


    # Enter a parse tree produced by LuaParser#funcname.
    def enterFuncname(self, ctx:LuaParser.FuncnameContext):
        pass

    # Exit a parse tree produced by LuaParser#funcname.
    def exitFuncname(self, ctx:LuaParser.FuncnameContext):
        pass


    # Enter a parse tree produced by LuaParser#varlist.
    def enterVarlist(self, ctx:LuaParser.VarlistContext):
        pass

    # Exit a parse tree produced by LuaParser#varlist.
    def exitVarlist(self, ctx:LuaParser.VarlistContext):
        pass


    # Enter a parse tree produced by LuaParser#namelist.
    def enterNamelist(self, ctx:LuaParser.NamelistContext):
        pass

    # Exit a parse tree produced by LuaParser#namelist.
    def exitNamelist(self, ctx:LuaParser.NamelistContext):
        pass


    # Enter a parse tree produced by LuaParser#name.
    def enterName(self, ctx:LuaParser.NameContext):
        pass

    # Exit a parse tree produced by LuaParser#name.
    def exitName(self, ctx:LuaParser.NameContext):
        pass


    # Enter a parse tree produced by LuaParser#explist.
    def enterExplist(self, ctx:LuaParser.ExplistContext):
        pass

    # Exit a parse tree produced by LuaParser#explist.
    def exitExplist(self, ctx:LuaParser.ExplistContext):
        pass


    # Enter a parse tree produced by LuaParser#bb.
    def enterBb(self, ctx:LuaParser.BbContext):
        pass

    # Exit a parse tree produced by LuaParser#bb.
    def exitBb(self, ctx:LuaParser.BbContext):
        pass


    # Enter a parse tree produced by LuaParser#unOpLength.
    def enterUnOpLength(self, ctx:LuaParser.UnOpLengthContext):
        pass

    # Exit a parse tree produced by LuaParser#unOpLength.
    def exitUnOpLength(self, ctx:LuaParser.UnOpLengthContext):
        pass


    # Enter a parse tree produced by LuaParser#relOpLessEq.
    def enterRelOpLessEq(self, ctx:LuaParser.RelOpLessEqContext):
        pass

    # Exit a parse tree produced by LuaParser#relOpLessEq.
    def exitRelOpLessEq(self, ctx:LuaParser.RelOpLessEqContext):
        pass


    # Enter a parse tree produced by LuaParser#bitOpOr.
    def enterBitOpOr(self, ctx:LuaParser.BitOpOrContext):
        pass

    # Exit a parse tree produced by LuaParser#bitOpOr.
    def exitBitOpOr(self, ctx:LuaParser.BitOpOrContext):
        pass


    # Enter a parse tree produced by LuaParser#opExpo.
    def enterOpExpo(self, ctx:LuaParser.OpExpoContext):
        pass

    # Exit a parse tree produced by LuaParser#opExpo.
    def exitOpExpo(self, ctx:LuaParser.OpExpoContext):
        pass


    # Enter a parse tree produced by LuaParser#relOpGreaterEq.
    def enterRelOpGreaterEq(self, ctx:LuaParser.RelOpGreaterEqContext):
        pass

    # Exit a parse tree produced by LuaParser#relOpGreaterEq.
    def exitRelOpGreaterEq(self, ctx:LuaParser.RelOpGreaterEqContext):
        pass


    # Enter a parse tree produced by LuaParser#opMult.
    def enterOpMult(self, ctx:LuaParser.OpMultContext):
        pass

    # Exit a parse tree produced by LuaParser#opMult.
    def exitOpMult(self, ctx:LuaParser.OpMultContext):
        pass


    # Enter a parse tree produced by LuaParser#bitOpAnd.
    def enterBitOpAnd(self, ctx:LuaParser.BitOpAndContext):
        pass

    # Exit a parse tree produced by LuaParser#bitOpAnd.
    def exitBitOpAnd(self, ctx:LuaParser.BitOpAndContext):
        pass


    # Enter a parse tree produced by LuaParser#bitOpShiftL.
    def enterBitOpShiftL(self, ctx:LuaParser.BitOpShiftLContext):
        pass

    # Exit a parse tree produced by LuaParser#bitOpShiftL.
    def exitBitOpShiftL(self, ctx:LuaParser.BitOpShiftLContext):
        pass


    # Enter a parse tree produced by LuaParser#loOpOr.
    def enterLoOpOr(self, ctx:LuaParser.LoOpOrContext):
        pass

    # Exit a parse tree produced by LuaParser#loOpOr.
    def exitLoOpOr(self, ctx:LuaParser.LoOpOrContext):
        pass


    # Enter a parse tree produced by LuaParser#unOpBitNot.
    def enterUnOpBitNot(self, ctx:LuaParser.UnOpBitNotContext):
        pass

    # Exit a parse tree produced by LuaParser#unOpBitNot.
    def exitUnOpBitNot(self, ctx:LuaParser.UnOpBitNotContext):
        pass


    # Enter a parse tree produced by LuaParser#bitOpXor.
    def enterBitOpXor(self, ctx:LuaParser.BitOpXorContext):
        pass

    # Exit a parse tree produced by LuaParser#bitOpXor.
    def exitBitOpXor(self, ctx:LuaParser.BitOpXorContext):
        pass


    # Enter a parse tree produced by LuaParser#opSub.
    def enterOpSub(self, ctx:LuaParser.OpSubContext):
        pass

    # Exit a parse tree produced by LuaParser#opSub.
    def exitOpSub(self, ctx:LuaParser.OpSubContext):
        pass


    # Enter a parse tree produced by LuaParser#bitOpShiftR.
    def enterBitOpShiftR(self, ctx:LuaParser.BitOpShiftRContext):
        pass

    # Exit a parse tree produced by LuaParser#bitOpShiftR.
    def exitBitOpShiftR(self, ctx:LuaParser.BitOpShiftRContext):
        pass


    # Enter a parse tree produced by LuaParser#nil.
    def enterNil(self, ctx:LuaParser.NilContext):
        pass

    # Exit a parse tree produced by LuaParser#nil.
    def exitNil(self, ctx:LuaParser.NilContext):
        pass


    # Enter a parse tree produced by LuaParser#opAdd.
    def enterOpAdd(self, ctx:LuaParser.OpAddContext):
        pass

    # Exit a parse tree produced by LuaParser#opAdd.
    def exitOpAdd(self, ctx:LuaParser.OpAddContext):
        pass


    # Enter a parse tree produced by LuaParser#opFloorDiv.
    def enterOpFloorDiv(self, ctx:LuaParser.OpFloorDivContext):
        pass

    # Exit a parse tree produced by LuaParser#opFloorDiv.
    def exitOpFloorDiv(self, ctx:LuaParser.OpFloorDivContext):
        pass


    # Enter a parse tree produced by LuaParser#number.
    def enterNumber(self, ctx:LuaParser.NumberContext):
        pass

    # Exit a parse tree produced by LuaParser#number.
    def exitNumber(self, ctx:LuaParser.NumberContext):
        pass


    # Enter a parse tree produced by LuaParser#relOpEq.
    def enterRelOpEq(self, ctx:LuaParser.RelOpEqContext):
        pass

    # Exit a parse tree produced by LuaParser#relOpEq.
    def exitRelOpEq(self, ctx:LuaParser.RelOpEqContext):
        pass


    # Enter a parse tree produced by LuaParser#relOpGreater.
    def enterRelOpGreater(self, ctx:LuaParser.RelOpGreaterContext):
        pass

    # Exit a parse tree produced by LuaParser#relOpGreater.
    def exitRelOpGreater(self, ctx:LuaParser.RelOpGreaterContext):
        pass


    # Enter a parse tree produced by LuaParser#relOpLess.
    def enterRelOpLess(self, ctx:LuaParser.RelOpLessContext):
        pass

    # Exit a parse tree produced by LuaParser#relOpLess.
    def exitRelOpLess(self, ctx:LuaParser.RelOpLessContext):
        pass


    # Enter a parse tree produced by LuaParser#table.
    def enterTable(self, ctx:LuaParser.TableContext):
        pass

    # Exit a parse tree produced by LuaParser#table.
    def exitTable(self, ctx:LuaParser.TableContext):
        pass


    # Enter a parse tree produced by LuaParser#ee.
    def enterEe(self, ctx:LuaParser.EeContext):
        pass

    # Exit a parse tree produced by LuaParser#ee.
    def exitEe(self, ctx:LuaParser.EeContext):
        pass


    # Enter a parse tree produced by LuaParser#unOpNot.
    def enterUnOpNot(self, ctx:LuaParser.UnOpNotContext):
        pass

    # Exit a parse tree produced by LuaParser#unOpNot.
    def exitUnOpNot(self, ctx:LuaParser.UnOpNotContext):
        pass


    # Enter a parse tree produced by LuaParser#unOpMin.
    def enterUnOpMin(self, ctx:LuaParser.UnOpMinContext):
        pass

    # Exit a parse tree produced by LuaParser#unOpMin.
    def exitUnOpMin(self, ctx:LuaParser.UnOpMinContext):
        pass


    # Enter a parse tree produced by LuaParser#opFloatDiv.
    def enterOpFloatDiv(self, ctx:LuaParser.OpFloatDivContext):
        pass

    # Exit a parse tree produced by LuaParser#opFloatDiv.
    def exitOpFloatDiv(self, ctx:LuaParser.OpFloatDivContext):
        pass


    # Enter a parse tree produced by LuaParser#todo6.
    def enterTodo6(self, ctx:LuaParser.Todo6Context):
        pass

    # Exit a parse tree produced by LuaParser#todo6.
    def exitTodo6(self, ctx:LuaParser.Todo6Context):
        pass


    # Enter a parse tree produced by LuaParser#false.
    def enterFalse(self, ctx:LuaParser.FalseContext):
        pass

    # Exit a parse tree produced by LuaParser#false.
    def exitFalse(self, ctx:LuaParser.FalseContext):
        pass


    # Enter a parse tree produced by LuaParser#concat.
    def enterConcat(self, ctx:LuaParser.ConcatContext):
        pass

    # Exit a parse tree produced by LuaParser#concat.
    def exitConcat(self, ctx:LuaParser.ConcatContext):
        pass


    # Enter a parse tree produced by LuaParser#loOpAnd.
    def enterLoOpAnd(self, ctx:LuaParser.LoOpAndContext):
        pass

    # Exit a parse tree produced by LuaParser#loOpAnd.
    def exitLoOpAnd(self, ctx:LuaParser.LoOpAndContext):
        pass


    # Enter a parse tree produced by LuaParser#opMod.
    def enterOpMod(self, ctx:LuaParser.OpModContext):
        pass

    # Exit a parse tree produced by LuaParser#opMod.
    def exitOpMod(self, ctx:LuaParser.OpModContext):
        pass


    # Enter a parse tree produced by LuaParser#true.
    def enterTrue(self, ctx:LuaParser.TrueContext):
        pass

    # Exit a parse tree produced by LuaParser#true.
    def exitTrue(self, ctx:LuaParser.TrueContext):
        pass


    # Enter a parse tree produced by LuaParser#relOpNotEq.
    def enterRelOpNotEq(self, ctx:LuaParser.RelOpNotEqContext):
        pass

    # Exit a parse tree produced by LuaParser#relOpNotEq.
    def exitRelOpNotEq(self, ctx:LuaParser.RelOpNotEqContext):
        pass


    # Enter a parse tree produced by LuaParser#todo5.
    def enterTodo5(self, ctx:LuaParser.Todo5Context):
        pass

    # Exit a parse tree produced by LuaParser#todo5.
    def exitTodo5(self, ctx:LuaParser.Todo5Context):
        pass


    # Enter a parse tree produced by LuaParser#todo2.
    def enterTodo2(self, ctx:LuaParser.Todo2Context):
        pass

    # Exit a parse tree produced by LuaParser#todo2.
    def exitTodo2(self, ctx:LuaParser.Todo2Context):
        pass


    # Enter a parse tree produced by LuaParser#stringExp.
    def enterStringExp(self, ctx:LuaParser.StringExpContext):
        pass

    # Exit a parse tree produced by LuaParser#stringExp.
    def exitStringExp(self, ctx:LuaParser.StringExpContext):
        pass


    # Enter a parse tree produced by LuaParser#prefixexp.
    def enterPrefixexp(self, ctx:LuaParser.PrefixexpContext):
        pass

    # Exit a parse tree produced by LuaParser#prefixexp.
    def exitPrefixexp(self, ctx:LuaParser.PrefixexpContext):
        pass


    # Enter a parse tree produced by LuaParser#varOrExp.
    def enterVarOrExp(self, ctx:LuaParser.VarOrExpContext):
        pass

    # Exit a parse tree produced by LuaParser#varOrExp.
    def exitVarOrExp(self, ctx:LuaParser.VarOrExpContext):
        pass


    # Enter a parse tree produced by LuaParser#var.
    def enterVar(self, ctx:LuaParser.VarContext):
        pass

    # Exit a parse tree produced by LuaParser#var.
    def exitVar(self, ctx:LuaParser.VarContext):
        pass


    # Enter a parse tree produced by LuaParser#varSuffix.
    def enterVarSuffix(self, ctx:LuaParser.VarSuffixContext):
        pass

    # Exit a parse tree produced by LuaParser#varSuffix.
    def exitVarSuffix(self, ctx:LuaParser.VarSuffixContext):
        pass


    # Enter a parse tree produced by LuaParser#nameAndArgs.
    def enterNameAndArgs(self, ctx:LuaParser.NameAndArgsContext):
        pass

    # Exit a parse tree produced by LuaParser#nameAndArgs.
    def exitNameAndArgs(self, ctx:LuaParser.NameAndArgsContext):
        pass


    # Enter a parse tree produced by LuaParser#args.
    def enterArgs(self, ctx:LuaParser.ArgsContext):
        pass

    # Exit a parse tree produced by LuaParser#args.
    def exitArgs(self, ctx:LuaParser.ArgsContext):
        pass


    # Enter a parse tree produced by LuaParser#functiondef.
    def enterFunctiondef(self, ctx:LuaParser.FunctiondefContext):
        pass

    # Exit a parse tree produced by LuaParser#functiondef.
    def exitFunctiondef(self, ctx:LuaParser.FunctiondefContext):
        pass


    # Enter a parse tree produced by LuaParser#funcbody.
    def enterFuncbody(self, ctx:LuaParser.FuncbodyContext):
        pass

    # Exit a parse tree produced by LuaParser#funcbody.
    def exitFuncbody(self, ctx:LuaParser.FuncbodyContext):
        pass


    # Enter a parse tree produced by LuaParser#parlist.
    def enterParlist(self, ctx:LuaParser.ParlistContext):
        pass

    # Exit a parse tree produced by LuaParser#parlist.
    def exitParlist(self, ctx:LuaParser.ParlistContext):
        pass


    # Enter a parse tree produced by LuaParser#tableconstructor.
    def enterTableconstructor(self, ctx:LuaParser.TableconstructorContext):
        pass

    # Exit a parse tree produced by LuaParser#tableconstructor.
    def exitTableconstructor(self, ctx:LuaParser.TableconstructorContext):
        pass


    # Enter a parse tree produced by LuaParser#field.
    def enterField(self, ctx:LuaParser.FieldContext):
        pass

    # Exit a parse tree produced by LuaParser#field.
    def exitField(self, ctx:LuaParser.FieldContext):
        pass


    # Enter a parse tree produced by LuaParser#tableKey.
    def enterTableKey(self, ctx:LuaParser.TableKeyContext):
        pass

    # Exit a parse tree produced by LuaParser#tableKey.
    def exitTableKey(self, ctx:LuaParser.TableKeyContext):
        pass


    # Enter a parse tree produced by LuaParser#tableValue.
    def enterTableValue(self, ctx:LuaParser.TableValueContext):
        pass

    # Exit a parse tree produced by LuaParser#tableValue.
    def exitTableValue(self, ctx:LuaParser.TableValueContext):
        pass


    # Enter a parse tree produced by LuaParser#fieldsep.
    def enterFieldsep(self, ctx:LuaParser.FieldsepContext):
        pass

    # Exit a parse tree produced by LuaParser#fieldsep.
    def exitFieldsep(self, ctx:LuaParser.FieldsepContext):
        pass


    # Enter a parse tree produced by LuaParser#string.
    def enterString(self, ctx:LuaParser.StringContext):
        pass

    # Exit a parse tree produced by LuaParser#string.
    def exitString(self, ctx:LuaParser.StringContext):
        pass


