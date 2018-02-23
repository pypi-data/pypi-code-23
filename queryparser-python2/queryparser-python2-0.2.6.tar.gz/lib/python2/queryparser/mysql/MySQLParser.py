# Generated from src/queryparser/mysql/MySQLParser.g4 by ANTLR 4.7
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write(u"\u0283\u036e\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6")
        buf.write(u"\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4")
        buf.write(u"\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t")
        buf.write(u"\22\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27")
        buf.write(u"\4\30\t\30\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4")
        buf.write(u"\35\t\35\4\36\t\36\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t")
        buf.write(u"#\4$\t$\4%\t%\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4")
        buf.write(u",\t,\4-\t-\4.\t.\4/\t/\4\60\t\60\4\61\t\61\4\62\t\62")
        buf.write(u"\4\63\t\63\4\64\t\64\4\65\t\65\4\66\t\66\4\67\t\67\4")
        buf.write(u"8\t8\49\t9\4:\t:\4;\t;\4<\t<\4=\t=\4>\t>\4?\t?\4@\t@")
        buf.write(u"\4A\tA\4B\tB\4C\tC\4D\tD\4E\tE\4F\tF\4G\tG\4H\tH\4I\t")
        buf.write(u"I\4J\tJ\4K\tK\4L\tL\4M\tM\4N\tN\4O\tO\4P\tP\4Q\tQ\3\2")
        buf.write(u"\3\2\3\3\3\3\3\3\3\3\5\3\u00a9\n\3\3\3\3\3\3\3\3\3\5")
        buf.write(u"\3\u00af\n\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\5\3\u00b8\n")
        buf.write(u"\3\3\3\5\3\u00bb\n\3\3\3\3\3\5\3\u00bf\n\3\3\3\3\3\3")
        buf.write(u"\3\5\3\u00c4\n\3\5\3\u00c6\n\3\3\4\3\4\3\4\3\4\3\4\3")
        buf.write(u"\4\3\4\5\4\u00cf\n\4\3\4\3\4\3\4\3\4\3\4\3\4\5\4\u00d7")
        buf.write(u"\n\4\3\5\3\5\3\6\3\6\3\7\3\7\3\b\3\b\3\t\3\t\3\n\5\n")
        buf.write(u"\u00e4\n\n\3\n\3\n\3\13\3\13\3\f\3\f\3\r\3\r\3\16\3\16")
        buf.write(u"\3\17\3\17\3\20\3\20\3\21\3\21\3\22\3\22\3\23\3\23\3")
        buf.write(u"\23\3\23\3\23\3\23\5\23\u00fe\n\23\3\24\3\24\3\24\3\24")
        buf.write(u"\3\24\3\24\5\24\u0106\n\24\3\25\3\25\5\25\u010a\n\25")
        buf.write(u"\3\25\5\25\u010d\n\25\3\25\5\25\u0110\n\25\3\25\5\25")
        buf.write(u"\u0113\n\25\3\25\5\25\u0116\n\25\3\25\5\25\u0119\n\25")
        buf.write(u"\3\25\5\25\u011c\n\25\3\25\5\25\u011f\n\25\3\25\3\25")
        buf.write(u"\3\25\3\25\5\25\u0125\n\25\3\25\5\25\u0128\n\25\3\25")
        buf.write(u"\5\25\u012b\n\25\3\25\5\25\u012e\n\25\5\25\u0130\n\25")
        buf.write(u"\3\25\5\25\u0133\n\25\3\25\5\25\u0136\n\25\3\25\3\25")
        buf.write(u"\3\25\3\25\3\25\3\25\5\25\u013e\n\25\3\25\5\25\u0141")
        buf.write(u"\n\25\3\26\5\26\u0144\n\26\3\26\3\26\3\27\3\27\3\27\5")
        buf.write(u"\27\u014b\n\27\3\30\3\30\3\30\3\30\5\30\u0151\n\30\3")
        buf.write(u"\30\5\30\u0154\n\30\3\30\3\30\5\30\u0158\n\30\3\31\3")
        buf.write(u"\31\3\31\5\31\u015d\n\31\3\31\3\31\5\31\u0161\n\31\3")
        buf.write(u"\31\3\31\3\32\3\32\3\32\3\32\3\32\6\32\u016a\n\32\r\32")
        buf.write(u"\16\32\u016b\3\33\3\33\3\33\3\33\3\33\3\33\6\33\u0174")
        buf.write(u"\n\33\r\33\16\33\u0175\3\34\3\34\3\34\3\34\7\34\u017c")
        buf.write(u"\n\34\f\34\16\34\u017f\13\34\3\34\3\34\3\35\3\35\3\36")
        buf.write(u"\3\36\3\36\5\36\u0188\n\36\3\36\3\36\3\36\5\36\u018d")
        buf.write(u"\n\36\3\36\3\36\3\37\3\37\3\37\3\37\3\37\3\37\5\37\u0197")
        buf.write(u"\n\37\5\37\u0199\n\37\3 \3 \3 \7 \u019e\n \f \16 \u01a1")
        buf.write(u"\13 \3!\3!\3!\7!\u01a6\n!\f!\16!\u01a9\13!\3\"\5\"\u01ac")
        buf.write(u"\n\"\3\"\3\"\3#\3#\3#\5#\u01b3\n#\3#\3#\5#\u01b7\n#\5")
        buf.write(u"#\u01b9\n#\3$\3$\3$\7$\u01be\n$\f$\16$\u01c1\13$\3%\3")
        buf.write(u"%\3%\3%\7%\u01c7\n%\f%\16%\u01ca\13%\3%\3%\3&\3&\3&\5")
        buf.write(u"&\u01d1\n&\3\'\3\'\3\'\5\'\u01d6\n\'\3(\3(\3(\7(\u01db")
        buf.write(u"\n(\f(\16(\u01de\13(\3)\3)\3)\7)\u01e3\n)\f)\16)\u01e6")
        buf.write(u"\13)\3*\5*\u01e9\n*\3*\3*\3*\5*\u01ee\n*\3+\3+\3+\3+")
        buf.write(u"\3+\7+\u01f5\n+\f+\16+\u01f8\13+\5+\u01fa\n+\3+\5+\u01fd")
        buf.write(u"\n+\3+\3+\3+\3+\3+\3+\3+\3+\3+\3+\3+\3+\3+\3+\3+\3+\3")
        buf.write(u"+\3+\3+\3+\3+\3+\3+\3+\5+\u0217\n+\3+\5+\u021a\n+\3+")
        buf.write(u"\3+\5+\u021e\n+\3,\3,\3,\3,\3,\7,\u0225\n,\f,\16,\u0228")
        buf.write(u"\13,\3,\3,\5,\u022c\n,\3-\3-\3-\5-\u0231\n-\3-\5-\u0234")
        buf.write(u"\n-\3.\3.\3.\3/\3/\3/\3/\5/\u023d\n/\3/\3/\3/\3/\3/\3")
        buf.write(u"/\3/\3/\3/\3/\3/\3/\3/\3/\5/\u024d\n/\3\60\3\60\3\60")
        buf.write(u"\7\60\u0252\n\60\f\60\16\60\u0255\13\60\3\61\3\61\3\62")
        buf.write(u"\3\62\3\62\7\62\u025c\n\62\f\62\16\62\u025f\13\62\3\63")
        buf.write(u"\3\63\3\63\3\63\3\63\3\63\3\63\5\63\u0268\n\63\5\63\u026a")
        buf.write(u"\n\63\3\64\3\64\3\64\3\64\3\65\3\65\3\65\3\65\5\65\u0274")
        buf.write(u"\n\65\3\66\3\66\3\66\3\66\5\66\u027a\n\66\3\66\3\66\3")
        buf.write(u"\66\3\66\3\66\5\66\u0281\n\66\3\67\3\67\3\67\3\67\7\67")
        buf.write(u"\u0287\n\67\f\67\16\67\u028a\13\67\3\67\3\67\3\67\5\67")
        buf.write(u"\u028f\n\67\38\38\39\39\3:\3:\3:\3:\3:\7:\u029a\n:\f")
        buf.write(u":\16:\u029d\13:\3;\3;\5;\u02a1\n;\3<\3<\3<\3<\3<\3=\3")
        buf.write(u"=\3>\3>\3>\7>\u02ad\n>\f>\16>\u02b0\13>\3?\5?\u02b3\n")
        buf.write(u"?\3?\3?\3?\5?\u02b8\n?\3?\3?\3?\3?\5?\u02be\n?\3?\3?")
        buf.write(u"\3?\3?\3?\3?\3?\5?\u02c7\n?\3@\3@\3@\3@\3A\3A\3A\5A\u02d0")
        buf.write(u"\nA\3B\3B\3B\3C\3C\3D\3D\3D\7D\u02da\nD\fD\16D\u02dd")
        buf.write(u"\13D\3D\3D\3D\3D\3D\7D\u02e4\nD\fD\16D\u02e7\13D\5D\u02e9")
        buf.write(u"\nD\5D\u02eb\nD\3E\3E\3E\5E\u02f0\nE\3E\7E\u02f3\nE\f")
        buf.write(u"E\16E\u02f6\13E\3F\3F\3F\3F\3F\3F\3F\3F\3F\3F\3F\3F\3")
        buf.write(u"F\5F\u0305\nF\3G\3G\3G\3G\3H\3H\5H\u030d\nH\3H\5H\u0310")
        buf.write(u"\nH\3H\5H\u0313\nH\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3")
        buf.write(u"H\3H\3H\3H\3H\5H\u0325\nH\3I\3I\3J\3J\5J\u032b\nJ\3J")
        buf.write(u"\3J\3J\5J\u0330\nJ\7J\u0332\nJ\fJ\16J\u0335\13J\3K\3")
        buf.write(u"K\3K\3K\3K\5K\u033c\nK\5K\u033e\nK\3L\3L\3L\5L\u0343")
        buf.write(u"\nL\3L\3L\3L\3L\7L\u0349\nL\fL\16L\u034c\13L\3M\3M\3")
        buf.write(u"M\3M\5M\u0352\nM\5M\u0354\nM\3M\3M\5M\u0358\nM\3N\3N")
        buf.write(u"\3O\3O\3O\7O\u035f\nO\fO\16O\u0362\13O\3P\3P\3P\5P\u0367")
        buf.write(u"\nP\3P\3P\3Q\3Q\3Q\3Q\2\2R\2\4\6\b\n\f\16\20\22\24\26")
        buf.write(u"\30\32\34\36 \"$&(*,.\60\62\64\668:<>@BDFHJLNPRTVXZ\\")
        buf.write(u"^`bdfhjlnprtvxz|~\u0080\u0082\u0084\u0086\u0088\u008a")
        buf.write(u"\u008c\u008e\u0090\u0092\u0094\u0096\u0098\u009a\u009c")
        buf.write(u"\u009e\u00a0\2\31\4\2\u0262\u0265\u0279\u027a\13\2MQ")
        buf.write(u"\u0081\u0084\u00bd\u00bf\u00c3\u00c3\u00d9\u00d9\u00eb")
        buf.write(u"\u00ec\u0135\u0135\u013d\u013d\u013f\u013f\4\2\u009d")
        buf.write(u"\u009d\u012e\u012e\4\2ii\u011d\u011d\3\2\u0272\u0273")
        buf.write(u"\4\2\u027b\u027b\u027e\u027e\"\2\16\16\27\27\33\33%%")
        buf.write(u"\'\'+,]]ggjknnrr\177\177\u008d\u008e\u00a3\u00a4\u00a9")
        buf.write(u"\u00aa\u00af\u00b1\u00b6\u00b6\u00bc\u00bc\u00ca\u00ca")
        buf.write(u"\u00cf\u00cf\u00db\u00db\u00e1\u00e4\u00e8\u00e9\u00f7")
        buf.write(u"\u00f7\u00f9\u00f9\u0106\u0106\u0108\u0109\u0119\u0119")
        buf.write(u"\u011c\u011c\u0121\u0121\u0126\u0126\u0138\u0138\f\2")
        buf.write(u"\23\23\31\32\34\35\63\63{{\u00b9\u00b9\u00c0\u00c0\u0101")
        buf.write(u"\u0104\u010b\u010b\u0131\u0133\27\2\3\4\17\17\21\22#")
        buf.write(u"$..\61\62<<VVeell\u00a7\u00a7\u00ac\u00ae\u00c1\u00c1")
        buf.write(u"\u00d6\u00d8\u00dc\u00dd\u00e6\u00e6\u00f2\u00f2\u00f4")
        buf.write(u"\u00f4\u0100\u0100\u010f\u010f\u011e\u011e\"\2\7\b\24")
        buf.write(u"\24&&((**--@@BBTUXY^_ppyy\u0086\u0087\u008a\u008b\u0092")
        buf.write(u"\u0092\u0094\u0094\u009c\u009c\u00a9\u00a9\u00b6\u00b7")
        buf.write(u"\u00ba\u00ba\u00c5\u00c5\u00cd\u00cd\u00d3\u00d3\u00e0")
        buf.write(u"\u00e0\u00ea\u00ea\u00ef\u00ef\u00f6\u00f6\u010e\u010e")
        buf.write(u"\u0128\u0128\u012f\u0130\u0134\u0134\37\2\5\6\60\60?")
        buf.write(u"?AACCELhhstxx\u0081\u0081\u009b\u009b\u00b4\u00b5\u00bb")
        buf.write(u"\u00bb\u00bd\u00bd\u00c3\u00c4\u00c8\u00c8\u00d4\u00d5")
        buf.write(u"\u00d9\u00d9\u00eb\u00eb\u00ed\u00ed\u0107\u0107\u010a")
        buf.write(u"\u010a\u010d\u010d\u0111\u0117\u011a\u011b\u0123\u0123")
        buf.write(u"\u012b\u012d\u0135\u0137\u013d\u013e\3\2\u0140\u0253")
        buf.write(u"\3\2\u0254\u025b\4\2\n\nZ[\4\2\u00fc\u00fc\u00fe\u00fe")
        buf.write(u"\3\2\u0267\u0268\5\2\u025d\u025e\u026d\u026d\u0277\u0277")
        buf.write(u"\4\2\30\30\u0272\u0274\5\2\n\nZZ\u026d\u026d\4\2\r\r")
        buf.write(u"WW\4\2\u0089\u0089\u0097\u0097\4\2>>\u008c\u008c\4\2")
        buf.write(u"\u00a3\u00a3\u00e4\u00e4\2\u03ae\2\u00a2\3\2\2\2\4\u00c5")
        buf.write(u"\3\2\2\2\6\u00d6\3\2\2\2\b\u00d8\3\2\2\2\n\u00da\3\2")
        buf.write(u"\2\2\f\u00dc\3\2\2\2\16\u00de\3\2\2\2\20\u00e0\3\2\2")
        buf.write(u"\2\22\u00e3\3\2\2\2\24\u00e7\3\2\2\2\26\u00e9\3\2\2\2")
        buf.write(u"\30\u00eb\3\2\2\2\32\u00ed\3\2\2\2\34\u00ef\3\2\2\2\36")
        buf.write(u"\u00f1\3\2\2\2 \u00f3\3\2\2\2\"\u00f5\3\2\2\2$\u00fd")
        buf.write(u"\3\2\2\2&\u0105\3\2\2\2(\u0107\3\2\2\2*\u0143\3\2\2\2")
        buf.write(u",\u0147\3\2\2\2.\u0157\3\2\2\2\60\u0159\3\2\2\2\62\u0169")
        buf.write(u"\3\2\2\2\64\u016d\3\2\2\2\66\u0177\3\2\2\28\u0182\3\2")
        buf.write(u"\2\2:\u018c\3\2\2\2<\u0198\3\2\2\2>\u019a\3\2\2\2@\u01a2")
        buf.write(u"\3\2\2\2B\u01ab\3\2\2\2D\u01af\3\2\2\2F\u01ba\3\2\2\2")
        buf.write(u"H\u01c2\3\2\2\2J\u01cd\3\2\2\2L\u01d2\3\2\2\2N\u01d7")
        buf.write(u"\3\2\2\2P\u01df\3\2\2\2R\u01e8\3\2\2\2T\u021d\3\2\2\2")
        buf.write(u"V\u021f\3\2\2\2X\u0230\3\2\2\2Z\u0235\3\2\2\2\\\u024c")
        buf.write(u"\3\2\2\2^\u024e\3\2\2\2`\u0256\3\2\2\2b\u0258\3\2\2\2")
        buf.write(u"d\u0260\3\2\2\2f\u026b\3\2\2\2h\u0273\3\2\2\2j\u0280")
        buf.write(u"\3\2\2\2l\u0282\3\2\2\2n\u0290\3\2\2\2p\u0292\3\2\2\2")
        buf.write(u"r\u0294\3\2\2\2t\u029e\3\2\2\2v\u02a2\3\2\2\2x\u02a7")
        buf.write(u"\3\2\2\2z\u02a9\3\2\2\2|\u02b2\3\2\2\2~\u02c8\3\2\2\2")
        buf.write(u"\u0080\u02cc\3\2\2\2\u0082\u02d1\3\2\2\2\u0084\u02d4")
        buf.write(u"\3\2\2\2\u0086\u02ea\3\2\2\2\u0088\u02ec\3\2\2\2\u008a")
        buf.write(u"\u0304\3\2\2\2\u008c\u0306\3\2\2\2\u008e\u0324\3\2\2")
        buf.write(u"\2\u0090\u0326\3\2\2\2\u0092\u0328\3\2\2\2\u0094\u0336")
        buf.write(u"\3\2\2\2\u0096\u033f\3\2\2\2\u0098\u034d\3\2\2\2\u009a")
        buf.write(u"\u0359\3\2\2\2\u009c\u035b\3\2\2\2\u009e\u0366\3\2\2")
        buf.write(u"\2\u00a0\u036a\3\2\2\2\u00a2\u00a3\t\2\2\2\u00a3\3\3")
        buf.write(u"\2\2\2\u00a4\u00a8\7\30\2\2\u00a5\u00a6\7\u026f\2\2\u00a6")
        buf.write(u"\u00a7\7\u027b\2\2\u00a7\u00a9\7\u026e\2\2\u00a8\u00a5")
        buf.write(u"\3\2\2\2\u00a8\u00a9\3\2\2\2\u00a9\u00c6\3\2\2\2\u00aa")
        buf.write(u"\u00ae\7%\2\2\u00ab\u00ac\7\u026f\2\2\u00ac\u00ad\7\u027b")
        buf.write(u"\2\2\u00ad\u00af\7\u026e\2\2\u00ae\u00ab\3\2\2\2\u00ae")
        buf.write(u"\u00af\3\2\2\2\u00af\u00c6\3\2\2\2\u00b0\u00c6\7H\2\2")
        buf.write(u"\u00b1\u00c6\7D\2\2\u00b2\u00ba\7S\2\2\u00b3\u00b4\7")
        buf.write(u"\u026f\2\2\u00b4\u00b7\7\u027b\2\2\u00b5\u00b6\7\u026c")
        buf.write(u"\2\2\u00b6\u00b8\7\u027b\2\2\u00b7\u00b5\3\2\2\2\u00b7")
        buf.write(u"\u00b8\3\2\2\2\u00b8\u00b9\3\2\2\2\u00b9\u00bb\7\u026e")
        buf.write(u"\2\2\u00ba\u00b3\3\2\2\2\u00ba\u00bb\3\2\2\2\u00bb\u00c6")
        buf.write(u"\3\2\2\2\u00bc\u00be\7\u00f3\2\2\u00bd\u00bf\7\u008f")
        buf.write(u"\2\2\u00be\u00bd\3\2\2\2\u00be\u00bf\3\2\2\2\u00bf\u00c6")
        buf.write(u"\3\2\2\2\u00c0\u00c6\7\u0116\2\2\u00c1\u00c3\7\u0124")
        buf.write(u"\2\2\u00c2\u00c4\7\u008f\2\2\u00c3\u00c2\3\2\2\2\u00c3")
        buf.write(u"\u00c4\3\2\2\2\u00c4\u00c6\3\2\2\2\u00c5\u00a4\3\2\2")
        buf.write(u"\2\u00c5\u00aa\3\2\2\2\u00c5\u00b0\3\2\2\2\u00c5\u00b1")
        buf.write(u"\3\2\2\2\u00c5\u00b2\3\2\2\2\u00c5\u00bc\3\2\2\2\u00c5")
        buf.write(u"\u00c0\3\2\2\2\u00c5\u00c1\3\2\2\2\u00c6\5\3\2\2\2\u00c7")
        buf.write(u"\u00c8\7\u0091\2\2\u00c8\u00c9\7\u00c6\2\2\u00c9\u00ca")
        buf.write(u"\7\u009a\2\2\u00ca\u00ce\7\u00c2\2\2\u00cb\u00cc\7\u013b")
        buf.write(u"\2\2\u00cc\u00cd\7\u00da\2\2\u00cd\u00cf\7f\2\2\u00ce")
        buf.write(u"\u00cb\3\2\2\2\u00ce\u00cf\3\2\2\2\u00cf\u00d7\3\2\2")
        buf.write(u"\2\u00d0\u00d1\7\u0091\2\2\u00d1\u00d2\7\36\2\2\u00d2")
        buf.write(u"\u00d7\7\u00c2\2\2\u00d3\u00d4\7\u013b\2\2\u00d4\u00d5")
        buf.write(u"\7\u00da\2\2\u00d5\u00d7\7f\2\2\u00d6\u00c7\3\2\2\2\u00d6")
        buf.write(u"\u00d0\3\2\2\2\u00d6\u00d3\3\2\2\2\u00d7\7\3\2\2\2\u00d8")
        buf.write(u"\u00d9\t\3\2\2\u00d9\t\3\2\2\2\u00da\u00db\t\4\2\2\u00db")
        buf.write(u"\13\3\2\2\2\u00dc\u00dd\7\u027d\2\2\u00dd\r\3\2\2\2\u00de")
        buf.write(u"\u00df\t\5\2\2\u00df\17\3\2\2\2\u00e0\u00e1\7\u027c\2")
        buf.write(u"\2\u00e1\21\3\2\2\2\u00e2\u00e4\t\6\2\2\u00e3\u00e2\3")
        buf.write(u"\2\2\2\u00e3\u00e4\3\2\2\2\u00e4\u00e5\3\2\2\2\u00e5")
        buf.write(u"\u00e6\t\7\2\2\u00e6\23\3\2\2\2\u00e7\u00e8\7\u027f\2")
        buf.write(u"\2\u00e8\25\3\2\2\2\u00e9\u00ea\t\b\2\2\u00ea\27\3\2")
        buf.write(u"\2\2\u00eb\u00ec\t\t\2\2\u00ec\31\3\2\2\2\u00ed\u00ee")
        buf.write(u"\t\n\2\2\u00ee\33\3\2\2\2\u00ef\u00f0\t\13\2\2\u00f0")
        buf.write(u"\35\3\2\2\2\u00f1\u00f2\t\f\2\2\u00f2\37\3\2\2\2\u00f3")
        buf.write(u"\u00f4\t\r\2\2\u00f4!\3\2\2\2\u00f5\u00f6\t\16\2\2\u00f6")
        buf.write(u"#\3\2\2\2\u00f7\u00fe\5\32\16\2\u00f8\u00fe\5\26\f\2")
        buf.write(u"\u00f9\u00fe\5\36\20\2\u00fa\u00fe\5\34\17\2\u00fb\u00fe")
        buf.write(u"\5 \21\2\u00fc\u00fe\5\"\22\2\u00fd\u00f7\3\2\2\2\u00fd")
        buf.write(u"\u00f8\3\2\2\2\u00fd\u00f9\3\2\2\2\u00fd\u00fa\3\2\2")
        buf.write(u"\2\u00fd\u00fb\3\2\2\2\u00fd\u00fc\3\2\2\2\u00fe%\3\2")
        buf.write(u"\2\2\u00ff\u0106\5\24\13\2\u0100\u0106\5\22\n\2\u0101")
        buf.write(u"\u0106\5\20\t\2\u0102\u0106\5\16\b\2\u0103\u0106\5\f")
        buf.write(u"\7\2\u0104\u0106\7\u00c9\2\2\u0105\u00ff\3\2\2\2\u0105")
        buf.write(u"\u0100\3\2\2\2\u0105\u0101\3\2\2\2\u0105\u0102\3\2\2")
        buf.write(u"\2\u0105\u0103\3\2\2\2\u0105\u0104\3\2\2\2\u0106\'\3")
        buf.write(u"\2\2\2\u0107\u0109\7\u00ee\2\2\u0108\u010a\t\17\2\2\u0109")
        buf.write(u"\u0108\3\2\2\2\u0109\u010a\3\2\2\2\u010a\u010c\3\2\2")
        buf.write(u"\2\u010b\u010d\7\u0080\2\2\u010c\u010b\3\2\2\2\u010c")
        buf.write(u"\u010d\3\2\2\2\u010d\u010f\3\2\2\2\u010e\u0110\7\u0105")
        buf.write(u"\2\2\u010f\u010e\3\2\2\2\u010f\u0110\3\2\2\2\u0110\u0112")
        buf.write(u"\3\2\2\2\u0111\u0113\7\u00ff\2\2\u0112\u0111\3\2\2\2")
        buf.write(u"\u0112\u0113\3\2\2\2\u0113\u0115\3\2\2\2\u0114\u0116")
        buf.write(u"\7\u00fa\2\2\u0115\u0114\3\2\2\2\u0115\u0116\3\2\2\2")
        buf.write(u"\u0116\u0118\3\2\2\2\u0117\u0119\7\u00fb\2\2\u0118\u0117")
        buf.write(u"\3\2\2\2\u0118\u0119\3\2\2\2\u0119\u011b\3\2\2\2\u011a")
        buf.write(u"\u011c\t\20\2\2\u011b\u011a\3\2\2\2\u011b\u011c\3\2\2")
        buf.write(u"\2\u011c\u011e\3\2\2\2\u011d\u011f\7\u00fd\2\2\u011e")
        buf.write(u"\u011d\3\2\2\2\u011e\u011f\3\2\2\2\u011f\u0120\3\2\2")
        buf.write(u"\2\u0120\u012f\5\u0086D\2\u0121\u0122\7q\2\2\u0122\u0124")
        buf.write(u"\5\u009cO\2\u0123\u0125\5v<\2\u0124\u0123\3\2\2\2\u0124")
        buf.write(u"\u0125\3\2\2\2\u0125\u0127\3\2\2\2\u0126\u0128\5\u00a0")
        buf.write(u"Q\2\u0127\u0126\3\2\2\2\u0127\u0128\3\2\2\2\u0128\u012a")
        buf.write(u"\3\2\2\2\u0129\u012b\5V,\2\u012a\u0129\3\2\2\2\u012a")
        buf.write(u"\u012b\3\2\2\2\u012b\u012d\3\2\2\2\u012c\u012e\5Z.\2")
        buf.write(u"\u012d\u012c\3\2\2\2\u012d\u012e\3\2\2\2\u012e\u0130")
        buf.write(u"\3\2\2\2\u012f\u0121\3\2\2\2\u012f\u0130\3\2\2\2\u0130")
        buf.write(u"\u0132\3\2\2\2\u0131\u0133\5r:\2\u0132\u0131\3\2\2\2")
        buf.write(u"\u0132\u0133\3\2\2\2\u0133\u0135\3\2\2\2\u0134\u0136")
        buf.write(u"\5j\66\2\u0135\u0134\3\2\2\2\u0135\u0136\3\2\2\2\u0136")
        buf.write(u"\u013d\3\2\2\2\u0137\u0138\7o\2\2\u0138\u013e\7\u0125")
        buf.write(u"\2\2\u0139\u013a\7\u00ab\2\2\u013a\u013b\7\u0091\2\2")
        buf.write(u"\u013b\u013c\7\u00f1\2\2\u013c\u013e\7\u00c2\2\2\u013d")
        buf.write(u"\u0137\3\2\2\2\u013d\u0139\3\2\2\2\u013d\u013e\3\2\2")
        buf.write(u"\2\u013e\u0140\3\2\2\2\u013f\u0141\7\u0269\2\2\u0140")
        buf.write(u"\u013f\3\2\2\2\u0140\u0141\3\2\2\2\u0141)\3\2\2\2\u0142")
        buf.write(u"\u0144\7\20\2\2\u0143\u0142\3\2\2\2\u0143\u0144\3\2\2")
        buf.write(u"\2\u0144\u0145\3\2\2\2\u0145\u0146\7\u0280\2\2\u0146")
        buf.write(u"+\3\2\2\2\u0147\u014a\5J&\2\u0148\u0149\7\u0275\2\2\u0149")
        buf.write(u"\u014b\5J&\2\u014a\u0148\3\2\2\2\u014a\u014b\3\2\2\2")
        buf.write(u"\u014b-\3\2\2\2\u014c\u0150\5\u0080A\2\u014d\u014e\5")
        buf.write(u"\2\2\2\u014e\u014f\5\u0080A\2\u014f\u0151\3\2\2\2\u0150")
        buf.write(u"\u014d\3\2\2\2\u0150\u0151\3\2\2\2\u0151\u0158\3\2\2")
        buf.write(u"\2\u0152\u0154\7\u00c7\2\2\u0153\u0152\3\2\2\2\u0153")
        buf.write(u"\u0154\3\2\2\2\u0154\u0155\3\2\2\2\u0155\u0156\7d\2\2")
        buf.write(u"\u0156\u0158\5\u008cG\2\u0157\u014c\3\2\2\2\u0157\u0153")
        buf.write(u"\3\2\2\2\u0158/\3\2\2\2\u0159\u015c\7!\2\2\u015a\u015d")
        buf.write(u"\5\62\32\2\u015b\u015d\5\64\33\2\u015c\u015a\3\2\2\2")
        buf.write(u"\u015c\u015b\3\2\2\2\u015d\u0160\3\2\2\2\u015e\u015f")
        buf.write(u"\7\\\2\2\u015f\u0161\5,\27\2\u0160\u015e\3\2\2\2\u0160")
        buf.write(u"\u0161\3\2\2\2\u0161\u0162\3\2\2\2\u0162\u0163\7`\2\2")
        buf.write(u"\u0163\61\3\2\2\2\u0164\u0165\7\u0139\2\2\u0165\u0166")
        buf.write(u"\5F$\2\u0166\u0167\7\u0110\2\2\u0167\u0168\5,\27\2\u0168")
        buf.write(u"\u016a\3\2\2\2\u0169\u0164\3\2\2\2\u016a\u016b\3\2\2")
        buf.write(u"\2\u016b\u0169\3\2\2\2\u016b\u016c\3\2\2\2\u016c\63\3")
        buf.write(u"\2\2\2\u016d\u0173\5,\27\2\u016e\u016f\7\u0139\2\2\u016f")
        buf.write(u"\u0170\5,\27\2\u0170\u0171\7\u0110\2\2\u0171\u0172\5")
        buf.write(u",\27\2\u0172\u0174\3\2\2\2\u0173\u016e\3\2\2\2\u0174")
        buf.write(u"\u0175\3\2\2\2\u0175\u0173\3\2\2\2\u0175\u0176\3\2\2")
        buf.write(u"\2\u0176\65\3\2\2\2\u0177\u0178\7\u026f\2\2\u0178\u017d")
        buf.write(u"\5:\36\2\u0179\u017a\7\u026c\2\2\u017a\u017c\5:\36\2")
        buf.write(u"\u017b\u0179\3\2\2\2\u017c\u017f\3\2\2\2\u017d\u017b")
        buf.write(u"\3\2\2\2\u017d\u017e\3\2\2\2\u017e\u0180\3\2\2\2\u017f")
        buf.write(u"\u017d\3\2\2\2\u0180\u0181\7\u026e\2\2\u0181\67\3\2\2")
        buf.write(u"\2\u0182\u0183\7\u0280\2\2\u01839\3\2\2\2\u0184\u0185")
        buf.write(u"\5\u0084C\2\u0185\u0186\7\u026b\2\2\u0186\u0188\3\2\2")
        buf.write(u"\2\u0187\u0184\3\2\2\2\u0187\u0188\3\2\2\2\u0188\u0189")
        buf.write(u"\3\2\2\2\u0189\u018a\5\u0090I\2\u018a\u018b\7\u026b\2")
        buf.write(u"\2\u018b\u018d\3\2\2\2\u018c\u0187\3\2\2\2\u018c\u018d")
        buf.write(u"\3\2\2\2\u018d\u018e\3\2\2\2\u018e\u018f\58\35\2\u018f")
        buf.write(u";\3\2\2\2\u0190\u0191\5\u009eP\2\u0191\u0192\7\u026b")
        buf.write(u"\2\2\u0192\u0193\7\u026d\2\2\u0193\u0199\3\2\2\2\u0194")
        buf.write(u"\u0196\5,\27\2\u0195\u0197\5*\26\2\u0196\u0195\3\2\2")
        buf.write(u"\2\u0196\u0197\3\2\2\2\u0197\u0199\3\2\2\2\u0198\u0190")
        buf.write(u"\3\2\2\2\u0198\u0194\3\2\2\2\u0199=\3\2\2\2\u019a\u019f")
        buf.write(u"\5@!\2\u019b\u019c\7\u013c\2\2\u019c\u019e\5@!\2\u019d")
        buf.write(u"\u019b\3\2\2\2\u019e\u01a1\3\2\2\2\u019f\u019d\3\2\2")
        buf.write(u"\2\u019f\u01a0\3\2\2\2\u01a0?\3\2\2\2\u01a1\u019f\3\2")
        buf.write(u"\2\2\u01a2\u01a7\5B\"\2\u01a3\u01a4\7\u0260\2\2\u01a4")
        buf.write(u"\u01a6\5B\"\2\u01a5\u01a3\3\2\2\2\u01a6\u01a9\3\2\2\2")
        buf.write(u"\u01a7\u01a5\3\2\2\2\u01a7\u01a8\3\2\2\2\u01a8A\3\2\2")
        buf.write(u"\2\u01a9\u01a7\3\2\2\2\u01aa\u01ac\7\u00c7\2\2\u01ab")
        buf.write(u"\u01aa\3\2\2\2\u01ab\u01ac\3\2\2\2\u01ac\u01ad\3\2\2")
        buf.write(u"\2\u01ad\u01ae\5D#\2\u01aeC\3\2\2\2\u01af\u01b8\5.\30")
        buf.write(u"\2\u01b0\u01b2\7\u0093\2\2\u01b1\u01b3\7\u00c7\2\2\u01b2")
        buf.write(u"\u01b1\3\2\2\2\u01b2\u01b3\3\2\2\2\u01b3\u01b6\3\2\2")
        buf.write(u"\2\u01b4\u01b7\5\16\b\2\u01b5\u01b7\7\u00c9\2\2\u01b6")
        buf.write(u"\u01b4\3\2\2\2\u01b6\u01b5\3\2\2\2\u01b7\u01b9\3\2\2")
        buf.write(u"\2\u01b8\u01b0\3\2\2\2\u01b8\u01b9\3\2\2\2\u01b9E\3\2")
        buf.write(u"\2\2\u01ba\u01bf\5> \2\u01bb\u01bc\7\u025f\2\2\u01bc")
        buf.write(u"\u01be\5> \2\u01bd\u01bb\3\2\2\2\u01be\u01c1\3\2\2\2")
        buf.write(u"\u01bf\u01bd\3\2\2\2\u01bf\u01c0\3\2\2\2\u01c0G\3\2\2")
        buf.write(u"\2\u01c1\u01bf\3\2\2\2\u01c2\u01c3\7\u026f\2\2\u01c3")
        buf.write(u"\u01c8\5F$\2\u01c4\u01c5\7\u026c\2\2\u01c5\u01c7\5F$")
        buf.write(u"\2\u01c6\u01c4\3\2\2\2\u01c7\u01ca\3\2\2\2\u01c8\u01c6")
        buf.write(u"\3\2\2\2\u01c8\u01c9\3\2\2\2\u01c9\u01cb\3\2\2\2\u01ca")
        buf.write(u"\u01c8\3\2\2\2\u01cb\u01cc\7\u026e\2\2\u01ccI\3\2\2\2")
        buf.write(u"\u01cd\u01d0\5L\'\2\u01ce\u01cf\7\u0276\2\2\u01cf\u01d1")
        buf.write(u"\5L\'\2\u01d0\u01ce\3\2\2\2\u01d0\u01d1\3\2\2\2\u01d1")
        buf.write(u"K\3\2\2\2\u01d2\u01d5\5N(\2\u01d3\u01d4\t\21\2\2\u01d4")
        buf.write(u"\u01d6\5N(\2\u01d5\u01d3\3\2\2\2\u01d5\u01d6\3\2\2\2")
        buf.write(u"\u01d6M\3\2\2\2\u01d7\u01dc\5P)\2\u01d8\u01d9\t\6\2\2")
        buf.write(u"\u01d9\u01db\5P)\2\u01da\u01d8\3\2\2\2\u01db\u01de\3")
        buf.write(u"\2\2\2\u01dc\u01da\3\2\2\2\u01dc\u01dd\3\2\2\2\u01dd")
        buf.write(u"O\3\2\2\2\u01de\u01dc\3\2\2\2\u01df\u01e4\5R*\2\u01e0")
        buf.write(u"\u01e1\t\22\2\2\u01e1\u01e3\5R*\2\u01e2\u01e0\3\2\2\2")
        buf.write(u"\u01e3\u01e6\3\2\2\2\u01e4\u01e2\3\2\2\2\u01e4\u01e5")
        buf.write(u"\3\2\2\2\u01e5Q\3\2\2\2\u01e6\u01e4\3\2\2\2\u01e7\u01e9")
        buf.write(u"\t\23\2\2\u01e8\u01e7\3\2\2\2\u01e8\u01e9\3\2\2\2\u01e9")
        buf.write(u"\u01ea\3\2\2\2\u01ea\u01ed\5\u008aF\2\u01eb\u01ec\t\6")
        buf.write(u"\2\2\u01ec\u01ee\5f\64\2\u01ed\u01eb\3\2\2\2\u01ed\u01ee")
        buf.write(u"\3\2\2\2\u01eeS\3\2\2\2\u01ef\u01fc\5$\23\2\u01f0\u01f9")
        buf.write(u"\7\u026f\2\2\u01f1\u01f6\5F$\2\u01f2\u01f3\7\u026c\2")
        buf.write(u"\2\u01f3\u01f5\5F$\2\u01f4\u01f2\3\2\2\2\u01f5\u01f8")
        buf.write(u"\3\2\2\2\u01f6\u01f4\3\2\2\2\u01f6\u01f7\3\2\2\2\u01f7")
        buf.write(u"\u01fa\3\2\2\2\u01f8\u01f6\3\2\2\2\u01f9\u01f1\3\2\2")
        buf.write(u"\2\u01f9\u01fa\3\2\2\2\u01fa\u01fb\3\2\2\2\u01fb\u01fd")
        buf.write(u"\7\u026e\2\2\u01fc\u01f0\3\2\2\2\u01fc\u01fd\3\2\2\2")
        buf.write(u"\u01fd\u021e\3\2\2\2\u01fe\u01ff\7/\2\2\u01ff\u0200\7")
        buf.write(u"\u026f\2\2\u0200\u0201\5F$\2\u0201\u0202\7\u026c\2\2")
        buf.write(u"\u0202\u0203\5\4\3\2\u0203\u0204\7\u026e\2\2\u0204\u021e")
        buf.write(u"\3\2\2\2\u0205\u0206\7/\2\2\u0206\u0207\7\u026f\2\2\u0207")
        buf.write(u"\u0208\5F$\2\u0208\u0209\7\u012a\2\2\u0209\u020a\5\n")
        buf.write(u"\6\2\u020a\u020b\7\u026e\2\2\u020b\u021e\3\2\2\2\u020c")
        buf.write(u"\u020d\7\"\2\2\u020d\u020e\7\u026f\2\2\u020e\u020f\5")
        buf.write(u"F$\2\u020f\u0210\7\20\2\2\u0210\u0211\5\4\3\2\u0211\u0212")
        buf.write(u"\7\u026e\2\2\u0212\u021e\3\2\2\2\u0213\u0214\5\30\r\2")
        buf.write(u"\u0214\u0216\7\u026f\2\2\u0215\u0217\t\24\2\2\u0216\u0215")
        buf.write(u"\3\2\2\2\u0216\u0217\3\2\2\2\u0217\u0219\3\2\2\2\u0218")
        buf.write(u"\u021a\5,\27\2\u0219\u0218\3\2\2\2\u0219\u021a\3\2\2")
        buf.write(u"\2\u021a\u021b\3\2\2\2\u021b\u021c\7\u026e\2\2\u021c")
        buf.write(u"\u021e\3\2\2\2\u021d\u01ef\3\2\2\2\u021d\u01fe\3\2\2")
        buf.write(u"\2\u021d\u0205\3\2\2\2\u021d\u020c\3\2\2\2\u021d\u0213")
        buf.write(u"\3\2\2\2\u021eU\3\2\2\2\u021f\u0220\7|\2\2\u0220\u0221")
        buf.write(u"\7\37\2\2\u0221\u0226\5X-\2\u0222\u0223\7\u026c\2\2\u0223")
        buf.write(u"\u0225\5X-\2\u0224\u0222\3\2\2\2\u0225\u0228\3\2\2\2")
        buf.write(u"\u0226\u0224\3\2\2\2\u0226\u0227\3\2\2\2\u0227\u022b")
        buf.write(u"\3\2\2\2\u0228\u0226\3\2\2\2\u0229\u022a\7\u013b\2\2")
        buf.write(u"\u022a\u022c\7\u00e5\2\2\u022b\u0229\3\2\2\2\u022b\u022c")
        buf.write(u"\3\2\2\2\u022cW\3\2\2\2\u022d\u0231\5:\36\2\u022e\u0231")
        buf.write(u"\7\u027b\2\2\u022f\u0231\5,\27\2\u0230\u022d\3\2\2\2")
        buf.write(u"\u0230\u022e\3\2\2\2\u0230\u022f\3\2\2\2\u0231\u0233")
        buf.write(u"\3\2\2\2\u0232\u0234\t\25\2\2\u0233\u0232\3\2\2\2\u0233")
        buf.write(u"\u0234\3\2\2\2\u0234Y\3\2\2\2\u0235\u0236\7}\2\2\u0236")
        buf.write(u"\u0237\5F$\2\u0237[\3\2\2\2\u0238\u0239\7\u0129\2\2\u0239")
        buf.write(u"\u023a\5d\63\2\u023a\u023c\7\u026f\2\2\u023b\u023d\5")
        buf.write(u"b\62\2\u023c\u023b\3\2\2\2\u023c\u023d\3\2\2\2\u023d")
        buf.write(u"\u023e\3\2\2\2\u023e\u023f\7\u026e\2\2\u023f\u024d\3")
        buf.write(u"\2\2\2\u0240\u0241\7\u0088\2\2\u0241\u0242\5d\63\2\u0242")
        buf.write(u"\u0243\7\u026f\2\2\u0243\u0244\5b\62\2\u0244\u0245\7")
        buf.write(u"\u026e\2\2\u0245\u024d\3\2\2\2\u0246\u0247\7m\2\2\u0247")
        buf.write(u"\u0248\5d\63\2\u0248\u0249\7\u026f\2\2\u0249\u024a\5")
        buf.write(u"b\62\2\u024a\u024b\7\u026e\2\2\u024b\u024d\3\2\2\2\u024c")
        buf.write(u"\u0238\3\2\2\2\u024c\u0240\3\2\2\2\u024c\u0246\3\2\2")
        buf.write(u"\2\u024d]\3\2\2\2\u024e\u0253\5\\/\2\u024f\u0250\7\u026c")
        buf.write(u"\2\2\u0250\u0252\5\\/\2\u0251\u024f\3\2\2\2\u0252\u0255")
        buf.write(u"\3\2\2\2\u0253\u0251\3\2\2\2\u0253\u0254\3\2\2\2\u0254")
        buf.write(u"_\3\2\2\2\u0255\u0253\3\2\2\2\u0256\u0257\7\u0280\2\2")
        buf.write(u"\u0257a\3\2\2\2\u0258\u025d\5`\61\2\u0259\u025a\7\u026c")
        buf.write(u"\2\2\u025a\u025c\5`\61\2\u025b\u0259\3\2\2\2\u025c\u025f")
        buf.write(u"\3\2\2\2\u025d\u025b\3\2\2\2\u025d\u025e\3\2\2\2\u025e")
        buf.write(u"c\3\2\2\2\u025f\u025d\3\2\2\2\u0260\u0269\t\26\2\2\u0261")
        buf.write(u"\u0267\7o\2\2\u0262\u0268\7\u0095\2\2\u0263\u0264\7\u00d0")
        buf.write(u"\2\2\u0264\u0268\7\37\2\2\u0265\u0266\7|\2\2\u0266\u0268")
        buf.write(u"\7\37\2\2\u0267\u0262\3\2\2\2\u0267\u0263\3\2\2\2\u0267")
        buf.write(u"\u0265\3\2\2\2\u0268\u026a\3\2\2\2\u0269\u0261\3\2\2")
        buf.write(u"\2\u0269\u026a\3\2\2\2\u026ae\3\2\2\2\u026b\u026c\7\u0090")
        buf.write(u"\2\2\u026c\u026d\5F$\2\u026d\u026e\5\b\5\2\u026eg\3\2")
        buf.write(u"\2\2\u026f\u0270\7\u00ce\2\2\u0270\u0274\5F$\2\u0271")
        buf.write(u"\u0272\7\u012a\2\2\u0272\u0274\5\66\34\2\u0273\u026f")
        buf.write(u"\3\2\2\2\u0273\u0271\3\2\2\2\u0274i\3\2\2\2\u0275\u0279")
        buf.write(u"\7\u00a6\2\2\u0276\u0277\5n8\2\u0277\u0278\7\u026c\2")
        buf.write(u"\2\u0278\u027a\3\2\2\2\u0279\u0276\3\2\2\2\u0279\u027a")
        buf.write(u"\3\2\2\2\u027a\u027b\3\2\2\2\u027b\u0281\5p9\2\u027c")
        buf.write(u"\u027d\5p9\2\u027d\u027e\7\u00cb\2\2\u027e\u027f\5n8")
        buf.write(u"\2\u027f\u0281\3\2\2\2\u0280\u0275\3\2\2\2\u0280\u027c")
        buf.write(u"\3\2\2\2\u0281k\3\2\2\2\u0282\u0283\7\u00b8\2\2\u0283")
        buf.write(u"\u0288\5:\36\2\u0284\u0285\7\u026c\2\2\u0285\u0287\5")
        buf.write(u":\36\2\u0286\u0284\3\2\2\2\u0287\u028a\3\2\2\2\u0288")
        buf.write(u"\u0286\3\2\2\2\u0288\u0289\3\2\2\2\u0289\u028b\3\2\2")
        buf.write(u"\2\u028a\u0288\3\2\2\2\u028b\u028c\7\t\2\2\u028c\u028e")
        buf.write(u"\5F$\2\u028d\u028f\5\6\4\2\u028e\u028d\3\2\2\2\u028e")
        buf.write(u"\u028f\3\2\2\2\u028fm\3\2\2\2\u0290\u0291\7\u027b\2\2")
        buf.write(u"\u0291o\3\2\2\2\u0292\u0293\7\u027b\2\2\u0293q\3\2\2")
        buf.write(u"\2\u0294\u0295\7\u00d0\2\2\u0295\u0296\7\37\2\2\u0296")
        buf.write(u"\u029b\5t;\2\u0297\u0298\7\u026c\2\2\u0298\u029a\5t;")
        buf.write(u"\2\u0299\u0297\3\2\2\2\u029a\u029d\3\2\2\2\u029b\u0299")
        buf.write(u"\3\2\2\2\u029b\u029c\3\2\2\2\u029cs\3\2\2\2\u029d\u029b")
        buf.write(u"\3\2\2\2\u029e\u02a0\5X-\2\u029f\u02a1\t\25\2\2\u02a0")
        buf.write(u"\u029f\3\2\2\2\u02a0\u02a1\3\2\2\2\u02a1u\3\2\2\2\u02a2")
        buf.write(u"\u02a3\7\u00d2\2\2\u02a3\u02a4\7\u026f\2\2\u02a4\u02a5")
        buf.write(u"\5z>\2\u02a5\u02a6\7\u026e\2\2\u02a6w\3\2\2\2\u02a7\u02a8")
        buf.write(u"\7\u0280\2\2\u02a8y\3\2\2\2\u02a9\u02ae\5x=\2\u02aa\u02ab")
        buf.write(u"\7\u026c\2\2\u02ab\u02ad\5x=\2\u02ac\u02aa\3\2\2\2\u02ad")
        buf.write(u"\u02b0\3\2\2\2\u02ae\u02ac\3\2\2\2\u02ae\u02af\3\2\2")
        buf.write(u"\2\u02af{\3\2\2\2\u02b0\u02ae\3\2\2\2\u02b1\u02b3\7\u00c7")
        buf.write(u"\2\2\u02b2\u02b1\3\2\2\2\u02b2\u02b3\3\2\2\2\u02b3\u02c6")
        buf.write(u"\3\2\2\2\u02b4\u02b7\7\u0091\2\2\u02b5\u02b8\5\u008c")
        buf.write(u"G\2\u02b6\u02b8\5H%\2\u02b7\u02b5\3\2\2\2\u02b7\u02b6")
        buf.write(u"\3\2\2\2\u02b8\u02c7\3\2\2\2\u02b9\u02ba\7\u00a5\2\2")
        buf.write(u"\u02ba\u02bd\5\u008aF\2\u02bb\u02bc\7a\2\2\u02bc\u02be")
        buf.write(u"\5\u008aF\2\u02bd\u02bb\3\2\2\2\u02bd\u02be\3\2\2\2\u02be")
        buf.write(u"\u02c7\3\2\2\2\u02bf\u02c0\7\u00df\2\2\u02c0\u02c7\5")
        buf.write(u",\27\2\u02c1\u02c2\7\25\2\2\u02c2\u02c3\5,\27\2\u02c3")
        buf.write(u"\u02c4\7\u0260\2\2\u02c4\u02c5\5\u0080A\2\u02c5\u02c7")
        buf.write(u"\3\2\2\2\u02c6\u02b4\3\2\2\2\u02c6\u02b9\3\2\2\2\u02c6")
        buf.write(u"\u02bf\3\2\2\2\u02c6\u02c1\3\2\2\2\u02c7}\3\2\2\2\u02c8")
        buf.write(u"\u02c9\7\u00f8\2\2\u02c9\u02ca\7\u00a5\2\2\u02ca\u02cb")
        buf.write(u"\5,\27\2\u02cb\177\3\2\2\2\u02cc\u02cf\5,\27\2\u02cd")
        buf.write(u"\u02d0\5|?\2\u02ce\u02d0\5~@\2\u02cf\u02cd\3\2\2\2\u02cf")
        buf.write(u"\u02ce\3\2\2\2\u02cf\u02d0\3\2\2\2\u02d0\u0081\3\2\2")
        buf.write(u"\2\u02d1\u02d2\5\u0088E\2\u02d2\u02d3\7\u0269\2\2\u02d3")
        buf.write(u"\u0083\3\2\2\2\u02d4\u02d5\7\u0280\2\2\u02d5\u0085\3")
        buf.write(u"\2\2\2\u02d6\u02db\5<\37\2\u02d7\u02d8\7\u026c\2\2\u02d8")
        buf.write(u"\u02da\5<\37\2\u02d9\u02d7\3\2\2\2\u02da\u02dd\3\2\2")
        buf.write(u"\2\u02db\u02d9\3\2\2\2\u02db\u02dc\3\2\2\2\u02dc\u02eb")
        buf.write(u"\3\2\2\2\u02dd\u02db\3\2\2\2\u02de\u02e8\7\u026d\2\2")
        buf.write(u"\u02df\u02e0\7\u026c\2\2\u02e0\u02e5\5<\37\2\u02e1\u02e2")
        buf.write(u"\7\u026c\2\2\u02e2\u02e4\5<\37\2\u02e3\u02e1\3\2\2\2")
        buf.write(u"\u02e4\u02e7\3\2\2\2\u02e5\u02e3\3\2\2\2\u02e5\u02e6")
        buf.write(u"\3\2\2\2\u02e6\u02e9\3\2\2\2\u02e7\u02e5\3\2\2\2\u02e8")
        buf.write(u"\u02df\3\2\2\2\u02e8\u02e9\3\2\2\2\u02e9\u02eb\3\2\2")
        buf.write(u"\2\u02ea\u02d6\3\2\2\2\u02ea\u02de\3\2\2\2\u02eb\u0087")
        buf.write(u"\3\2\2\2\u02ec\u02f4\5(\25\2\u02ed\u02ef\7\u0122\2\2")
        buf.write(u"\u02ee\u02f0\7\n\2\2\u02ef\u02ee\3\2\2\2\u02ef\u02f0")
        buf.write(u"\3\2\2\2\u02f0\u02f1\3\2\2\2\u02f1\u02f3\5(\25\2\u02f2")
        buf.write(u"\u02ed\3\2\2\2\u02f3\u02f6\3\2\2\2\u02f4\u02f2\3\2\2")
        buf.write(u"\2\u02f4\u02f5\3\2\2\2\u02f5\u0089\3\2\2\2\u02f6\u02f4")
        buf.write(u"\3\2\2\2\u02f7\u0305\5&\24\2\u02f8\u0305\5H%\2\u02f9")
        buf.write(u"\u0305\5:\36\2\u02fa\u0305\5T+\2\u02fb\u0305\7\u0283")
        buf.write(u"\2\2\u02fc\u02fd\7\u00e7\2\2\u02fd\u0305\5H%\2\u02fe")
        buf.write(u"\u0305\5\u008cG\2\u02ff\u0300\7d\2\2\u0300\u0305\5\u008c")
        buf.write(u"G\2\u0301\u0305\5f\64\2\u0302\u0305\5l\67\2\u0303\u0305")
        buf.write(u"\5\60\31\2\u0304\u02f7\3\2\2\2\u0304\u02f8\3\2\2\2\u0304")
        buf.write(u"\u02f9\3\2\2\2\u0304\u02fa\3\2\2\2\u0304\u02fb\3\2\2")
        buf.write(u"\2\u0304\u02fc\3\2\2\2\u0304\u02fe\3\2\2\2\u0304\u02ff")
        buf.write(u"\3\2\2\2\u0304\u0301\3\2\2\2\u0304\u0302\3\2\2\2\u0304")
        buf.write(u"\u0303\3\2\2\2\u0305\u008b\3\2\2\2\u0306\u0307\7\u026f")
        buf.write(u"\2\2\u0307\u0308\5\u0088E\2\u0308\u0309\7\u026e\2\2\u0309")
        buf.write(u"\u008d\3\2\2\2\u030a\u030c\5\u009eP\2\u030b\u030d\5v")
        buf.write(u"<\2\u030c\u030b\3\2\2\2\u030c\u030d\3\2\2\2\u030d\u030f")
        buf.write(u"\3\2\2\2\u030e\u0310\5*\26\2\u030f\u030e\3\2\2\2\u030f")
        buf.write(u"\u0310\3\2\2\2\u0310\u0312\3\2\2\2\u0311\u0313\5^\60")
        buf.write(u"\2\u0312\u0311\3\2\2\2\u0312\u0313\3\2\2\2\u0313\u0325")
        buf.write(u"\3\2\2\2\u0314\u0315\5\u008cG\2\u0315\u0316\5*\26\2\u0316")
        buf.write(u"\u0325\3\2\2\2\u0317\u0318\7\u026f\2\2\u0318\u0319\5")
        buf.write(u"\u009cO\2\u0319\u031a\7\u026e\2\2\u031a\u0325\3\2\2\2")
        buf.write(u"\u031b\u031c\7\u00cc\2\2\u031c\u031d\5\u009aN\2\u031d")
        buf.write(u"\u031e\7\u00a3\2\2\u031e\u031f\7\u00d1\2\2\u031f\u0320")
        buf.write(u"\7\u0095\2\2\u0320\u0321\5\u009aN\2\u0321\u0322\7\u00ce")
        buf.write(u"\2\2\u0322\u0323\5F$\2\u0323\u0325\3\2\2\2\u0324\u030a")
        buf.write(u"\3\2\2\2\u0324\u0314\3\2\2\2\u0324\u0317\3\2\2\2\u0324")
        buf.write(u"\u031b\3\2\2\2\u0325\u008f\3\2\2\2\u0326\u0327\7\u0280")
        buf.write(u"\2\2\u0327\u0091\3\2\2\2\u0328\u0333\5\u0094K\2\u0329")
        buf.write(u"\u032b\t\27\2\2\u032a\u0329\3\2\2\2\u032a\u032b\3\2\2")
        buf.write(u"\2\u032b\u032c\3\2\2\2\u032c\u032d\7\u0095\2\2\u032d")
        buf.write(u"\u032f\5\u008eH\2\u032e\u0330\5h\65\2\u032f\u032e\3\2")
        buf.write(u"\2\2\u032f\u0330\3\2\2\2\u0330\u0332\3\2\2\2\u0331\u032a")
        buf.write(u"\3\2\2\2\u0332\u0335\3\2\2\2\u0333\u0331\3\2\2\2\u0333")
        buf.write(u"\u0334\3\2\2\2\u0334\u0093\3\2\2\2\u0335\u0333\3\2\2")
        buf.write(u"\2\u0336\u033d\5\u0096L\2\u0337\u0338\7\u0105\2\2\u0338")
        buf.write(u"\u033b\5\u008eH\2\u0339\u033a\7\u00ce\2\2\u033a\u033c")
        buf.write(u"\5F$\2\u033b\u0339\3\2\2\2\u033b\u033c\3\2\2\2\u033c")
        buf.write(u"\u033e\3\2\2\2\u033d\u0337\3\2\2\2\u033d\u033e\3\2\2")
        buf.write(u"\2\u033e\u0095\3\2\2\2\u033f\u034a\5\u0098M\2\u0340\u0342")
        buf.write(u"\t\30\2\2\u0341\u0343\7\u00d1\2\2\u0342\u0341\3\2\2\2")
        buf.write(u"\u0342\u0343\3\2\2\2\u0343\u0344\3\2\2\2\u0344\u0345")
        buf.write(u"\7\u0095\2\2\u0345\u0346\5\u0098M\2\u0346\u0347\5h\65")
        buf.write(u"\2\u0347\u0349\3\2\2\2\u0348\u0340\3\2\2\2\u0349\u034c")
        buf.write(u"\3\2\2\2\u034a\u0348\3\2\2\2\u034a\u034b\3\2\2\2\u034b")
        buf.write(u"\u0097\3\2\2\2\u034c\u034a\3\2\2\2\u034d\u0357\5\u008e")
        buf.write(u"H\2\u034e\u0353\7\u00c6\2\2\u034f\u0351\t\30\2\2\u0350")
        buf.write(u"\u0352\7\u00d1\2\2\u0351\u0350\3\2\2\2\u0351\u0352\3")
        buf.write(u"\2\2\2\u0352\u0354\3\2\2\2\u0353\u034f\3\2\2\2\u0353")
        buf.write(u"\u0354\3\2\2\2\u0354\u0355\3\2\2\2\u0355\u0356\7\u0095")
        buf.write(u"\2\2\u0356\u0358\5\u008eH\2\u0357\u034e\3\2\2\2\u0357")
        buf.write(u"\u0358\3\2\2\2\u0358\u0099\3\2\2\2\u0359\u035a\5\u0092")
        buf.write(u"J\2\u035a\u009b\3\2\2\2\u035b\u0360\5\u009aN\2\u035c")
        buf.write(u"\u035d\7\u026c\2\2\u035d\u035f\5\u009aN\2\u035e\u035c")
        buf.write(u"\3\2\2\2\u035f\u0362\3\2\2\2\u0360\u035e\3\2\2\2\u0360")
        buf.write(u"\u0361\3\2\2\2\u0361\u009d\3\2\2\2\u0362\u0360\3\2\2")
        buf.write(u"\2\u0363\u0364\5\u0084C\2\u0364\u0365\7\u026b\2\2\u0365")
        buf.write(u"\u0367\3\2\2\2\u0366\u0363\3\2\2\2\u0366\u0367\3\2\2")
        buf.write(u"\2\u0367\u0368\3\2\2\2\u0368\u0369\5\u0090I\2\u0369\u009f")
        buf.write(u"\3\2\2\2\u036a\u036b\7\u013a\2\2\u036b\u036c\5F$\2\u036c")
        buf.write(u"\u00a1\3\2\2\2o\u00a8\u00ae\u00b7\u00ba\u00be\u00c3\u00c5")
        buf.write(u"\u00ce\u00d6\u00e3\u00fd\u0105\u0109\u010c\u010f\u0112")
        buf.write(u"\u0115\u0118\u011b\u011e\u0124\u0127\u012a\u012d\u012f")
        buf.write(u"\u0132\u0135\u013d\u0140\u0143\u014a\u0150\u0153\u0157")
        buf.write(u"\u015c\u0160\u016b\u0175\u017d\u0187\u018c\u0196\u0198")
        buf.write(u"\u019f\u01a7\u01ab\u01b2\u01b6\u01b8\u01bf\u01c8\u01d0")
        buf.write(u"\u01d5\u01dc\u01e4\u01e8\u01ed\u01f6\u01f9\u01fc\u0216")
        buf.write(u"\u0219\u021d\u0226\u022b\u0230\u0233\u023c\u024c\u0253")
        buf.write(u"\u025d\u0267\u0269\u0273\u0279\u0280\u0288\u028e\u029b")
        buf.write(u"\u02a0\u02ae\u02b2\u02b7\u02bd\u02c6\u02cf\u02db\u02e5")
        buf.write(u"\u02e8\u02ea\u02ef\u02f4\u0304\u030c\u030f\u0312\u0324")
        buf.write(u"\u032a\u032f\u0333\u033b\u033d\u0342\u034a\u0351\u0353")
        buf.write(u"\u0357\u0360\u0366")
        return buf.getvalue()


class MySQLParser ( Parser ):

    grammarFileName = "MySQLParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"'USER'", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"'=>'", 
                     u"<INVALID>", u"<INVALID>", u"'<='", u"'>='", u"':='", 
                     u"'<<'", u"'>>'", u"';'", u"':'", u"'.'", u"','", u"'*'", 
                     u"')'", u"'('", u"']'", u"'['", u"'+'", u"'-'", u"'~'", 
                     u"'|'", u"'&'", u"'^'", u"'`'", u"'>'", u"'<'" ]

    symbolicNames = [ u"<INVALID>", u"ABS", u"ACOS", u"ADDDATE", u"ADDTIME", 
                      u"AES_DECRYPT", u"AES_ENCRYPT", u"AGAINST", u"ALL", 
                      u"ANY", u"ARMSCII8", u"ASC", u"ASCII_SYM", u"ASIN", 
                      u"AS_SYM", u"ATAN", u"ATAN2", u"AVG", u"BENCHMARK", 
                      u"BETWEEN", u"BIG5", u"BIN", u"BINARY", u"BIT_AND", 
                      u"BIT_COUNT", u"BIT_LENGTH", u"BIT_OR", u"BIT_XOR", 
                      u"BOOLEAN_SYM", u"BY_SYM", u"CACHE_SYM", u"CASE_SYM", 
                      u"CAST_SYM", u"CEIL", u"CEILING", u"CHAR", u"CHARSET", 
                      u"CHAR_LENGTH", u"COERCIBILITY", u"COLLATE_SYM", u"COLLATION", 
                      u"CONCAT", u"CONCAT_WS", u"CONNECTION_ID", u"CONV", 
                      u"CONVERT_SYM", u"CONVERT_TZ", u"COS", u"COT", u"COUNT", 
                      u"CP1250", u"CP1251", u"CP1256", u"CP1257", u"CP850", 
                      u"CP852", u"CP866", u"CP932", u"CRC32", u"CROSECOND", 
                      u"CROSS", u"CURDATE", u"CURRENT_USER", u"CURTIME", 
                      u"DATABASE", u"DATEDIFF", u"DATETIME", u"DATE_ADD", 
                      u"DATE_FORMAT", u"DATE_SUB", u"DATE_SYM", u"DAYNAME", 
                      u"DAYOFMONTH", u"DAYOFWEEK", u"DAYOFYEAR", u"DAY_HOUR", 
                      u"DAY_MICROSECOND", u"DAY_MINUTE", u"DAY_SECOND", 
                      u"DAY_SYM", u"DEC8", u"DECIMAL_SYM", u"DECODE", u"DEFAULT", 
                      u"DEGREES", u"DESC", u"DES_DECRYPT", u"DES_ENCRYPT", 
                      u"DISTINCT", u"DISTINCTROW", u"ELSE_SYM", u"ELT", 
                      u"ENCODE", u"ENCRYPT", u"END_SYM", u"ESCAPE_SYM", 
                      u"EUCJPMS", u"EUCKR", u"EXISTS", u"EXP", u"EXPANSION_SYM", 
                      u"EXPORT_SET", u"EXTRACT", u"FALSE_SYM", u"FIELD", 
                      u"FIND_IN_SET", u"FLOOR", u"FORCE_SYM", u"FORMAT", 
                      u"FOR_SYM", u"FOUND_ROWS", u"FROM", u"FROM_BASE64", 
                      u"FROM_DAYS", u"FROM_UNIXTIME", u"GB2312", u"GBK", 
                      u"GEOSTD8", u"GET_FORMAT", u"GET_LOCK", u"GREEK", 
                      u"GROUP_CONCAT", u"GROUP_SYM", u"HAVING", u"HEBREW", 
                      u"HEX", u"HIGH_PRIORITY", u"HOUR", u"HOUR_MICROSECOND", 
                      u"HOUR_MINUTE", u"HOUR_SECOND", u"HP8", u"IF", u"IFNULL", 
                      u"IGNORE_SYM", u"INDEX_SYM", u"INET_ATON", u"INET_NTOA", 
                      u"INNER_SYM", u"INSERT", u"INSTR", u"INTEGER_SYM", 
                      u"INTERVAL_SYM", u"IN_SYM", u"IS_FREE_LOCK", u"IS_SYM", 
                      u"IS_USED_LOCK", u"JOIN_SYM", u"KEYBCS2", u"KEY_SYM", 
                      u"KOI8R", u"KOI8U", u"LANGUAGE", u"LAST_DAY", u"LAST_INSERT_ID", 
                      u"LATIN1", u"LATIN1_BIN", u"LATIN1_GENERAL_CS", u"LATIN2", 
                      u"LATIN5", u"LATIN7", u"LEFT", u"LENGTH", u"LIKE_SYM", 
                      u"LIMIT", u"LN", u"LOAD", u"LOAD_FILE", u"LOCATE", 
                      u"LOCK", u"LOG", u"LOG10", u"LOG2", u"LOWER", u"LPAD", 
                      u"LTRIM", u"MACCE", u"MACROMAN", u"MAKEDATE", u"MAKETIME", 
                      u"MAKE_SET", u"MASTER_POS_WAIT", u"MATCH", u"MAX_SYM", 
                      u"MD5", u"MICROSECOND", u"MID", u"MINUTE", u"MINUTE_MICROSECOND", 
                      u"MINUTE_SECOND", u"MIN_SYM", u"MOD", u"MODE_SYM", 
                      u"MONTH", u"MONTHNAME", u"NAME_CONST", u"NATURAL", 
                      u"NOT_SYM", u"NOW", u"NULL_SYM", u"OCT", u"OFFSET_SYM", 
                      u"OJ_SYM", u"OLD_PASSWORD", u"ON", u"ORD", u"ORDER_SYM", 
                      u"OUTER", u"PARTITION_SYM", u"PASSWORD", u"PERIOD_ADD", 
                      u"PERIOD_DIFF", u"PI", u"POW", u"POWER", u"QUARTER", 
                      u"QUERY_SYM", u"QUOTE", u"RADIANS", u"RAND", u"REAL", 
                      u"REGEXP", u"RELEASE_LOCK", u"REPEAT", u"REPLACE", 
                      u"REVERSE", u"RIGHT", u"ROLLUP_SYM", u"ROUND", u"ROW_SYM", 
                      u"RPAD", u"RTRIM", u"SCHEMA", u"SECOND", u"SECOND_MICROSECOND", 
                      u"SEC_TO_TIME", u"SELECT", u"SESSION_USER", u"SET_SYM", 
                      u"SHARE_SYM", u"SIGN", u"SIGNED_SYM", u"SIN", u"SJIS", 
                      u"SLEEP", u"SOUNDEX", u"SOUNDS_SYM", u"SPACE", u"SQL_BIG_RESULT", 
                      u"SQL_BUFFER_RESULT", u"SQL_CACHE_SYM", u"SQL_CALC_FOUND_ROWS", 
                      u"SQL_NO_CACHE_SYM", u"SQL_SMALL_RESULT", u"SQRT", 
                      u"STD", u"STDDEV", u"STDDEV_POP", u"STDDEV_SAMP", 
                      u"STRAIGHT_JOIN", u"STRCMP", u"STR_TO_DATE", u"SUBSTRING", 
                      u"SUBSTRING_INDEX", u"SUBTIME", u"SUM", u"SWE7", u"SYSDATE", 
                      u"SYSTEM_USER", u"TAN", u"THEN_SYM", u"TIMEDIFF", 
                      u"TIMESTAMP", u"TIMESTAMPADD", u"TIMESTAMPDIFF", u"TIME_FORMAT", 
                      u"TIME_SYM", u"TIME_TO_SEC", u"TIS620", u"TO_BASE64", 
                      u"TO_DAYS", u"TO_SECONDS", u"TRIM", u"TRUE_SYM", u"TRUNCATE", 
                      u"UCS2", u"UJIS", u"UNHEX", u"UNION_SYM", u"UNIX_TIMESTAMP", 
                      u"UNSIGNED_SYM", u"UPDATE", u"UPPER", u"USE", u"USER", 
                      u"USE_SYM", u"USING_SYM", u"UTC_DATE", u"UTC_TIME", 
                      u"UTC_TIMESTAMP", u"UTF8", u"UUID", u"VALUES", u"VARIANCE", 
                      u"VAR_POP", u"VAR_SAMP", u"VERSION_SYM", u"WEEK", 
                      u"WEEKDAY", u"WEEKOFYEAR", u"WEIGHT_STRING", u"WHEN_SYM", 
                      u"WHERE", u"WITH", u"XOR", u"YEAR", u"YEARWEEK", u"YEAR_MONTH", 
                      u"SDIST", u"SAREA", u"SCENTER", u"SCIRCUM", u"SLENGTH", 
                      u"SSWAP", u"SNPOINTS", u"SSTR", u"MYSQL_SPHERE_VERSION", 
                      u"SRCONTAINSL", u"SLCONTAINSR", u"SRNOTCONTAINSL", 
                      u"SLNOTCONTAINSR", u"SOVERLAPS", u"SNOTOVERLAPS", 
                      u"SEQUAL", u"SNOTEQUAL", u"STRANSFORM", u"SINVERSE", 
                      u"SPOINT", u"SPOINT_LONG", u"SPOINT_LAT", u"SPOINT_X", 
                      u"SPOINT_Y", u"SPOINT_Z", u"SPOINT_EQUAL", u"STRANS", 
                      u"STRANS_POINT", u"STRANS_POINT_INVERSE", u"STRANS_EQUAL", 
                      u"STRANS_EQUAL_NEG", u"STRANS_PHI", u"STRANS_THETA", 
                      u"STRANS_PSI", u"STRANS_AXES", u"STRANS_INVERT", u"STRANS_ZXZ", 
                      u"STRANS_TRANS", u"STRANS_TRANS_INV", u"SCIRCLE", 
                      u"SCIRCLE_RADIUS", u"SCIRCLE_EQUAL", u"SCIRCLE_EQUAL_NEG", 
                      u"SCIRCLE_OVERLAP", u"SCIRCLE_OVERLAP_NEG", u"SCIRCLE_CONTAINED_BY_CIRCLE", 
                      u"SCIRCLE_CONTAINED_BY_CIRCLE_NEG", u"SCIRCLE_CONTAINS_CIRCLE", 
                      u"SCIRCLE_CONTAINS_CIRCLE_NEG", u"SPOINT_CONTAINED_BY_CIRCLE", 
                      u"SPOINT_CONTAINED_BY_CIRCLE_NEG", u"SPOINT_CONTAINED_BY_CIRCLE_COM", 
                      u"SPOINT_CONTAINED_BY_CIRCLE_COM_NEG", u"STRANS_CIRCLE", 
                      u"STRANS_CIRCLE_INVERSE", u"SLINE", u"SMERIDIAN", 
                      u"SLINE_BEG", u"SLINE_END", u"SLINE_EQUAL", u"SLINE_EQUAL_NEG", 
                      u"SLINE_TURN", u"SLINE_CROSSES", u"SLINE_CROSSES_NEG", 
                      u"SLINE_OVERLAP", u"SLINE_CONTAINS_POINT", u"SLINE_CONTAINS_POINT_COM", 
                      u"SLINE_CONTAINS_POINT_NEG", u"SLINE_CONTAINS_POINT_COM_NEG", 
                      u"STRANS_LINE", u"STRANS_LINE_INVERSE", u"SLINE_OVERLAP_CIRCLE", 
                      u"SLINE_OVERLAP_CIRCLE_COM", u"SLINE_OVERLAP_CIRCLE_NEG", 
                      u"SLINE_OVERLAP_CIRCLE_COM_NEG", u"SCIRCLE_CONTAINS_LINE", 
                      u"SCIRCLE_CONTAINS_LINE_COM", u"SCIRCLE_CONTAINS_LINE_NEG", 
                      u"SCIRCLE_CONTAINS_LINE_COM_NEG", u"SELLIPSE", u"SELLIPSE_INC", 
                      u"SELLIPSE_LRAD", u"SELLIPSE_SRAD", u"SELLIPSE_EQUAL", 
                      u"SELLIPSE_EQUAL_NEG", u"SELLIPSE_CONTAINS_ELLIPSE", 
                      u"SELLIPSE_CONTAINS_ELLIPSE_NEG", u"SELLIPSE_CONTAINS_ELLIPSE_COM", 
                      u"SELLIPSE_CONTAINS_ELLIPSE_COM_NEG", u"SELLIPSE_OVERLAP_ELLIPSE", 
                      u"SELLIPSE_OVERLAP_ELLIPSE_NEG", u"SELLIPSE_CONTAINS_POINT", 
                      u"SELLIPSE_CONTAINS_POINT_NEG", u"SELLIPSE_CONTAINS_POINT_COM", 
                      u"SELLIPSE_CONTAINS_POINT_COM_NEG", u"SELLIPSE_CONTAINS_CIRCLE", 
                      u"SELLIPSE_CONTAINS_CIRCLE_NEG", u"SELLIPSE_CONTAINS_CIRCLE_COM", 
                      u"SELLIPSE_CONTAINS_CIRCLE_COM_NEG", u"SCIRCLE_CONTAINS_ELLIPSE", 
                      u"SCIRCLE_CONTAINS_ELLIPSE_NEG", u"SCIRCLE_CONTAINS_ELLIPSE_COM", 
                      u"SCIRCLE_CONTAINS_ELLIPSE_COM_NEG", u"SELLIPSE_OVERLAP_CIRCLE", 
                      u"SELLIPSE_OVERLAP_CIRCLE_NEG", u"SELLIPSE_OVERLAP_CIRCLE_COM", 
                      u"SELLIPSE_OVERLAP_CIRCLE_COM_NEG", u"SELLIPSE_OVERLAP_LINE", 
                      u"SELLIPSE_OVERLAP_LINE_NEG", u"SELLIPSE_OVERLAP_LINE_COM", 
                      u"SELLIPSE_OVERLAP_LINE_COM_NEG", u"SELLIPSE_CONTAINS_LINE", 
                      u"SELLIPSE_CONTAINS_LINE_NEG", u"SELLIPSE_CONTAINS_LINE_COM", 
                      u"SELLIPSE_CONTAINS_LINE_COM_NEG", u"STRANS_ELLIPSE", 
                      u"STRANS_ELLIPSE_INVERSE", u"SPOLY", u"SPOLY_EQUAL", 
                      u"SPOLY_EQUAL_NEG", u"SPOLY_CONTAINS_POLYGON", u"SPOLY_CONTAINS_POLYGON_NEG", 
                      u"SPOLY_CONTAINS_POLYGON_COM", u"SPOLY_CONTAINS_POLYGON_COM_NEG", 
                      u"SPOLY_OVERLAP_POLYGON", u"SPOLY_OVERLAP_POLYGON_NEG", 
                      u"SPOLY_CONTAINS_POINT", u"SPOLY_CONTAINS_POINT_NEG", 
                      u"SPOLY_CONTAINS_POINT_COM", u"SPOLY_CONTAINS_POINT_COM_NEG", 
                      u"SPOLY_CONTAINS_CIRCLE", u"SPOLY_CONTAINS_CIRCLE_NEG", 
                      u"SPOLY_CONTAINS_CIRCLE_COM", u"SPOLY_CONTAINS_CIRCLE_COM_NEG", 
                      u"SCIRCLE_CONTAINS_POLYGON", u"SCIRCLE_CONTAINS_POLYGON_NEG", 
                      u"SCIRCLE_CONTAINS_POLYGON_COM", u"SCIRCLE_CONTAINS_POLYGON_COM_NEG", 
                      u"SPOLY_OVERLAP_CIRCLE", u"SPOLY_OVERLAP_CIRCLE_NEG", 
                      u"SPOLY_OVERLAP_CIRCLE_COM", u"SPOLY_OVERLAP_CIRCLE_COM_NEG", 
                      u"SPOLY_CONTAINS_LINE", u"SPOLY_CONTAINS_LINE_NEG", 
                      u"SPOLY_CONTAINS_LINE_COM", u"SPOLY_CONTAINS_LINE_COM_NEG", 
                      u"SPOLY_OVERLAP_LINE", u"SPOLY_OVERLAP_LINE_NEG", 
                      u"SPOLY_OVERLAP_LINE_COM", u"SPOLY_OVERLAP_LINE_COM_NEG", 
                      u"SPOLY_CONTAINS_ELLIPSE", u"SPOLY_CONTAINS_ELLIPSE_NEG", 
                      u"SPOLY_CONTAINS_ELLIPSE_COM", u"SPOLY_CONTAINS_ELLIPSE_COM_NEG", 
                      u"SELLIPSE_CONTAINS_POLYGON", u"SELLIPSE_CONTAINS_POLYGON_NEG", 
                      u"SELLIPSE_CONTAINS_POLYGON_COM", u"SELLIPSE_CONTAINS_POLYGON_COM_NEG", 
                      u"SPOLY_OVERLAP_ELLIPSE", u"SPOLY_OVERLAP_ELLIPSE_NEG", 
                      u"SPOLY_OVERLAP_ELLIPSE_COM", u"SPOLY_OVERLAP_ELLIPSE_COM_NEG", 
                      u"STRANS_POLY", u"STRANS_POLY_INVERSE", u"SPOLY_ADD_POINT_AGGR", 
                      u"SPOLY_AGGR", u"SPATH", u"SPATH_EQUAL", u"SPATH_EQUAL_NEG", 
                      u"SPATH_OVERLAP_PATH", u"SPATH_OVERLAP_PATH_NEG", 
                      u"SPATH_CONTAINS_POINT", u"SPATH_CONTAINS_POINT_NEG", 
                      u"SPATH_CONTAINS_POINT_COM", u"SPATH_CONTAINS_POINT_COM_NEG", 
                      u"SCIRCLE_CONTAINS_PATH", u"SCIRCLE_CONTAINS_PATH_NEG", 
                      u"SCIRCLE_CONTAINS_PATH_COM", u"SCIRCLE_CONTAINS_PATH_COM_NEG", 
                      u"SCIRCLE_OVERLAP_PATH", u"SCIRCLE_OVERLAP_PATH_NEG", 
                      u"SCIRCLE_OVERLAP_PATH_COM", u"SCIRCLE_OVERLAP_PATH_COM_NEG", 
                      u"SPATH_OVERLAP_LINE", u"SPATH_OVERLAP_LINE_NEG", 
                      u"SPATH_OVERLAP_LINE_COM", u"SPATH_OVERLAP_LINE_COM_NEG", 
                      u"SELLIPSE_CONTAINS_PATH", u"SELLIPSE_CONTAINS_PATH_NEG", 
                      u"SELLIPSE_CONTAINS_PATH_COM", u"SELLIPSE_CONTAINS_PATH_COM_NEG", 
                      u"SELLIPSE_OVERLAP_PATH", u"SELLIPSE_OVERLAP_PATH_NEG", 
                      u"SELLIPSE_OVERLAP_PATH_COM", u"SELLIPSE_OVERLAP_PATH_COM_NEG", 
                      u"SPOLY_CONTAINS_PATH", u"SPOLY_CONTAINS_PATH_NEG", 
                      u"SPOLY_CONTAINS_PATH_COM", u"SPOLY_CONTAINS_PATH_COM_NEG", 
                      u"SPOLY_OVERLAP_PATH", u"SPOLY_OVERLAP_PATH_NEG", 
                      u"SPOLY_OVERLAP_PATH_COM", u"SPOLY_OVERLAP_PATH_COM_NEG", 
                      u"STRANS_PATH", u"STRANS_PATH_INVERSE", u"SPATH_ADD_POINT_AGGR", 
                      u"SPATH_AGGR", u"SBOX", u"SBOX_SW", u"SBOX_SE", u"SBOX_NW", 
                      u"SBOX_NE", u"SBOX_EQUAL", u"SBOX_EQUAL_NEG", u"SBOX_CONTAINS_BOX", 
                      u"SBOX_CONTAINS_BOX_NEG", u"SBOX_CONTAINS_BOX_COM", 
                      u"SBOX_CONTAINS_BOX_COM_NEG", u"SBOX_OVERLAP_BOX", 
                      u"SBOX_OVERLAP_BOX_NEG", u"SBOX_CONTAINS_POINT", u"SBOX_CONTAINS_POINT_NEG", 
                      u"SBOX_CONTAINS_POINT_COM", u"SBOX_CONTAINS_POINT_COM_NEG", 
                      u"SBOX_CONTAINS_CIRCLE", u"SBOX_CONTAINS_CIRCLE_NEG", 
                      u"SBOX_CONTAINS_CIRCLE_COM", u"SBOX_CONTAINS_CIRCLE_COM_NEG", 
                      u"SCIRCLE_CONTAINS_BOX", u"SCIRCLE_CONTAINS_BOX_NEG", 
                      u"SCIRCLE_CONTAINS_BOX_COM", u"SCIRCLE_CONTAINS_BOX_COM_NEG", 
                      u"SBOX_OVERLAP_CIRCLE", u"SBOX_OVERLAP_CIRCLE_NEG", 
                      u"SBOX_OVERLAP_CIRCLE_COM", u"SBOX_OVERLAP_CIRCLE_COM_NEG", 
                      u"SBOX_CONTAINS_LINE", u"SBOX_CONTAINS_LINE_NEG", 
                      u"SBOX_CONTAINS_LINE_COM", u"SBOX_CONTAINS_LINE_COM_NEG", 
                      u"SBOX_OVERLAP_LINE", u"SBOX_OVERLAP_LINE_NEG", u"SBOX_OVERLAP_LINE_COM", 
                      u"SBOX_OVERLAP_LINE_COM_NEG", u"SBOX_CONTAINS_ELLIPSE", 
                      u"SBOX_CONTAINS_ELLIPSE_NEG", u"SBOX_CONTAINS_ELLIPSE_COM", 
                      u"SBOX_CONTAINS_ELLIPSE_COM_NEG", u"SELLIPSE_CONTAINS_BOX", 
                      u"SELLIPSE_CONTAINS_BOX_NEG", u"SELLIPSE_CONTAINS_BOX_COM", 
                      u"SELLIPSE_CONTAINS_BOX_COM_NEG", u"SBOX_OVERLAP_ELLIPSE", 
                      u"SBOX_OVERLAP_ELLIPSE_NEG", u"SBOX_OVERLAP_ELLIPSE_COM", 
                      u"SBOX_OVERLAP_ELLIPSE_COM_NEG", u"SBOX_CONTAINS_POLY", 
                      u"SBOX_CONTAINS_POLY_NEG", u"SBOX_CONTAINS_POLY_COM", 
                      u"SBOX_CONTAINS_POLY_COM_NEG", u"SPOLY_CONTAINS_BOX", 
                      u"SPOLY_CONTAINS_BOX_NEG", u"SPOLY_CONTAINS_BOX_COM", 
                      u"SPOLY_CONTAINS_BOX_COM_NEG", u"SBOX_OVERLAP_POLY", 
                      u"SBOX_OVERLAP_POLY_NEG", u"SBOX_OVERLAP_POLY_COM", 
                      u"SBOX_OVERLAP_POLY_COM_NEG", u"SBOX_CONTAINS_PATH", 
                      u"SBOX_CONTAINS_PATH_NEG", u"SBOX_CONTAINS_PATH_COM", 
                      u"SBOX_CONTAINS_PATH_COM_NEG", u"SBOX_OVERLAP_PATH", 
                      u"SBOX_OVERLAP_PATH_NEG", u"SBOX_OVERLAP_PATH_COM", 
                      u"SBOX_OVERLAP_PATH_COM_NEG", u"STRRPOS", u"IDLE", 
                      u"ANGDIST", u"HILBERTKEY", u"COORDFROMHILBERTKEY", 
                      u"SUM_OF_SQUARES", u"PARTITADD_SUM_OF_SQARES", u"GAIA_HEALPIX", 
                      u"SPRNG_DBL", u"DIVIDE", u"MOD_SYM", u"OR_SYM", u"AND_SYM", 
                      u"ARROW", u"EQ", u"NOT_EQ", u"LET", u"GET", u"SET_VAR", 
                      u"SHIFT_LEFT", u"SHIFT_RIGHT", u"SEMI", u"COLON", 
                      u"DOT", u"COMMA", u"ASTERISK", u"RPAREN", u"LPAREN", 
                      u"RBRACK", u"LBRACK", u"PLUS", u"MINUS", u"NEGATION", 
                      u"VERTBAR", u"BITAND", u"POWER_OP", u"BACKTICK", u"GTH", 
                      u"LTH", u"INTEGER_NUM", u"HEX_DIGIT", u"BIT_NUM", 
                      u"REAL_NUMBER", u"TEXT_STRING", u"ID", u"COMMENT", 
                      u"WS", u"USER_VAR" ]

    RULE_relational_op = 0
    RULE_cast_data_type = 1
    RULE_search_modifier = 2
    RULE_interval_unit = 3
    RULE_transcoding_name = 4
    RULE_bit_literal = 5
    RULE_boolean_literal = 6
    RULE_hex_literal = 7
    RULE_number_literal = 8
    RULE_string_literal = 9
    RULE_char_functions = 10
    RULE_group_functions = 11
    RULE_number_functions = 12
    RULE_other_functions = 13
    RULE_time_functions = 14
    RULE_mysql_sphere_functions = 15
    RULE_mysql_udf_functions = 16
    RULE_functionList = 17
    RULE_literal_value = 18
    RULE_select_expression = 19
    RULE_alias = 20
    RULE_bit_expr = 21
    RULE_bool_primary = 22
    RULE_case_when_statement = 23
    RULE_case_when_statement1 = 24
    RULE_case_when_statement2 = 25
    RULE_column_list = 26
    RULE_column_name = 27
    RULE_column_spec = 28
    RULE_displayed_column = 29
    RULE_exp_factor1 = 30
    RULE_exp_factor2 = 31
    RULE_exp_factor3 = 32
    RULE_exp_factor4 = 33
    RULE_expression = 34
    RULE_expression_list = 35
    RULE_factor1 = 36
    RULE_factor2 = 37
    RULE_factor3 = 38
    RULE_factor4 = 39
    RULE_factor5 = 40
    RULE_function_call = 41
    RULE_groupby_clause = 42
    RULE_groupby_item = 43
    RULE_having_clause = 44
    RULE_index_hint = 45
    RULE_index_hint_list = 46
    RULE_index_name = 47
    RULE_index_list = 48
    RULE_index_options = 49
    RULE_interval_expr = 50
    RULE_join_condition = 51
    RULE_limit_clause = 52
    RULE_match_against_statement = 53
    RULE_offset = 54
    RULE_row_count = 55
    RULE_orderby_clause = 56
    RULE_orderby_item = 57
    RULE_partition_clause = 58
    RULE_partition_name = 59
    RULE_partition_names = 60
    RULE_bit_fac1 = 61
    RULE_bit_fac2 = 62
    RULE_predicate = 63
    RULE_query = 64
    RULE_schema_name = 65
    RULE_select_list = 66
    RULE_select_statement = 67
    RULE_simple_expr = 68
    RULE_subquery = 69
    RULE_table_atom = 70
    RULE_table_name = 71
    RULE_table_factor1 = 72
    RULE_table_factor2 = 73
    RULE_table_factor3 = 74
    RULE_table_factor4 = 75
    RULE_table_reference = 76
    RULE_table_references = 77
    RULE_table_spec = 78
    RULE_where_clause = 79

    ruleNames =  [ u"relational_op", u"cast_data_type", u"search_modifier", 
                   u"interval_unit", u"transcoding_name", u"bit_literal", 
                   u"boolean_literal", u"hex_literal", u"number_literal", 
                   u"string_literal", u"char_functions", u"group_functions", 
                   u"number_functions", u"other_functions", u"time_functions", 
                   u"mysql_sphere_functions", u"mysql_udf_functions", u"functionList", 
                   u"literal_value", u"select_expression", u"alias", u"bit_expr", 
                   u"bool_primary", u"case_when_statement", u"case_when_statement1", 
                   u"case_when_statement2", u"column_list", u"column_name", 
                   u"column_spec", u"displayed_column", u"exp_factor1", 
                   u"exp_factor2", u"exp_factor3", u"exp_factor4", u"expression", 
                   u"expression_list", u"factor1", u"factor2", u"factor3", 
                   u"factor4", u"factor5", u"function_call", u"groupby_clause", 
                   u"groupby_item", u"having_clause", u"index_hint", u"index_hint_list", 
                   u"index_name", u"index_list", u"index_options", u"interval_expr", 
                   u"join_condition", u"limit_clause", u"match_against_statement", 
                   u"offset", u"row_count", u"orderby_clause", u"orderby_item", 
                   u"partition_clause", u"partition_name", u"partition_names", 
                   u"bit_fac1", u"bit_fac2", u"predicate", u"query", u"schema_name", 
                   u"select_list", u"select_statement", u"simple_expr", 
                   u"subquery", u"table_atom", u"table_name", u"table_factor1", 
                   u"table_factor2", u"table_factor3", u"table_factor4", 
                   u"table_reference", u"table_references", u"table_spec", 
                   u"where_clause" ]

    EOF = Token.EOF
    ABS=1
    ACOS=2
    ADDDATE=3
    ADDTIME=4
    AES_DECRYPT=5
    AES_ENCRYPT=6
    AGAINST=7
    ALL=8
    ANY=9
    ARMSCII8=10
    ASC=11
    ASCII_SYM=12
    ASIN=13
    AS_SYM=14
    ATAN=15
    ATAN2=16
    AVG=17
    BENCHMARK=18
    BETWEEN=19
    BIG5=20
    BIN=21
    BINARY=22
    BIT_AND=23
    BIT_COUNT=24
    BIT_LENGTH=25
    BIT_OR=26
    BIT_XOR=27
    BOOLEAN_SYM=28
    BY_SYM=29
    CACHE_SYM=30
    CASE_SYM=31
    CAST_SYM=32
    CEIL=33
    CEILING=34
    CHAR=35
    CHARSET=36
    CHAR_LENGTH=37
    COERCIBILITY=38
    COLLATE_SYM=39
    COLLATION=40
    CONCAT=41
    CONCAT_WS=42
    CONNECTION_ID=43
    CONV=44
    CONVERT_SYM=45
    CONVERT_TZ=46
    COS=47
    COT=48
    COUNT=49
    CP1250=50
    CP1251=51
    CP1256=52
    CP1257=53
    CP850=54
    CP852=55
    CP866=56
    CP932=57
    CRC32=58
    CROSECOND=59
    CROSS=60
    CURDATE=61
    CURRENT_USER=62
    CURTIME=63
    DATABASE=64
    DATEDIFF=65
    DATETIME=66
    DATE_ADD=67
    DATE_FORMAT=68
    DATE_SUB=69
    DATE_SYM=70
    DAYNAME=71
    DAYOFMONTH=72
    DAYOFWEEK=73
    DAYOFYEAR=74
    DAY_HOUR=75
    DAY_MICROSECOND=76
    DAY_MINUTE=77
    DAY_SECOND=78
    DAY_SYM=79
    DEC8=80
    DECIMAL_SYM=81
    DECODE=82
    DEFAULT=83
    DEGREES=84
    DESC=85
    DES_DECRYPT=86
    DES_ENCRYPT=87
    DISTINCT=88
    DISTINCTROW=89
    ELSE_SYM=90
    ELT=91
    ENCODE=92
    ENCRYPT=93
    END_SYM=94
    ESCAPE_SYM=95
    EUCJPMS=96
    EUCKR=97
    EXISTS=98
    EXP=99
    EXPANSION_SYM=100
    EXPORT_SET=101
    EXTRACT=102
    FALSE_SYM=103
    FIELD=104
    FIND_IN_SET=105
    FLOOR=106
    FORCE_SYM=107
    FORMAT=108
    FOR_SYM=109
    FOUND_ROWS=110
    FROM=111
    FROM_BASE64=112
    FROM_DAYS=113
    FROM_UNIXTIME=114
    GB2312=115
    GBK=116
    GEOSTD8=117
    GET_FORMAT=118
    GET_LOCK=119
    GREEK=120
    GROUP_CONCAT=121
    GROUP_SYM=122
    HAVING=123
    HEBREW=124
    HEX=125
    HIGH_PRIORITY=126
    HOUR=127
    HOUR_MICROSECOND=128
    HOUR_MINUTE=129
    HOUR_SECOND=130
    HP8=131
    IF=132
    IFNULL=133
    IGNORE_SYM=134
    INDEX_SYM=135
    INET_ATON=136
    INET_NTOA=137
    INNER_SYM=138
    INSERT=139
    INSTR=140
    INTEGER_SYM=141
    INTERVAL_SYM=142
    IN_SYM=143
    IS_FREE_LOCK=144
    IS_SYM=145
    IS_USED_LOCK=146
    JOIN_SYM=147
    KEYBCS2=148
    KEY_SYM=149
    KOI8R=150
    KOI8U=151
    LANGUAGE=152
    LAST_DAY=153
    LAST_INSERT_ID=154
    LATIN1=155
    LATIN1_BIN=156
    LATIN1_GENERAL_CS=157
    LATIN2=158
    LATIN5=159
    LATIN7=160
    LEFT=161
    LENGTH=162
    LIKE_SYM=163
    LIMIT=164
    LN=165
    LOAD=166
    LOAD_FILE=167
    LOCATE=168
    LOCK=169
    LOG=170
    LOG10=171
    LOG2=172
    LOWER=173
    LPAD=174
    LTRIM=175
    MACCE=176
    MACROMAN=177
    MAKEDATE=178
    MAKETIME=179
    MAKE_SET=180
    MASTER_POS_WAIT=181
    MATCH=182
    MAX_SYM=183
    MD5=184
    MICROSECOND=185
    MID=186
    MINUTE=187
    MINUTE_MICROSECOND=188
    MINUTE_SECOND=189
    MIN_SYM=190
    MOD=191
    MODE_SYM=192
    MONTH=193
    MONTHNAME=194
    NAME_CONST=195
    NATURAL=196
    NOT_SYM=197
    NOW=198
    NULL_SYM=199
    OCT=200
    OFFSET_SYM=201
    OJ_SYM=202
    OLD_PASSWORD=203
    ON=204
    ORD=205
    ORDER_SYM=206
    OUTER=207
    PARTITION_SYM=208
    PASSWORD=209
    PERIOD_ADD=210
    PERIOD_DIFF=211
    PI=212
    POW=213
    POWER=214
    QUARTER=215
    QUERY_SYM=216
    QUOTE=217
    RADIANS=218
    RAND=219
    REAL=220
    REGEXP=221
    RELEASE_LOCK=222
    REPEAT=223
    REPLACE=224
    REVERSE=225
    RIGHT=226
    ROLLUP_SYM=227
    ROUND=228
    ROW_SYM=229
    RPAD=230
    RTRIM=231
    SCHEMA=232
    SECOND=233
    SECOND_MICROSECOND=234
    SEC_TO_TIME=235
    SELECT=236
    SESSION_USER=237
    SET_SYM=238
    SHARE_SYM=239
    SIGN=240
    SIGNED_SYM=241
    SIN=242
    SJIS=243
    SLEEP=244
    SOUNDEX=245
    SOUNDS_SYM=246
    SPACE=247
    SQL_BIG_RESULT=248
    SQL_BUFFER_RESULT=249
    SQL_CACHE_SYM=250
    SQL_CALC_FOUND_ROWS=251
    SQL_NO_CACHE_SYM=252
    SQL_SMALL_RESULT=253
    SQRT=254
    STD=255
    STDDEV=256
    STDDEV_POP=257
    STDDEV_SAMP=258
    STRAIGHT_JOIN=259
    STRCMP=260
    STR_TO_DATE=261
    SUBSTRING=262
    SUBSTRING_INDEX=263
    SUBTIME=264
    SUM=265
    SWE7=266
    SYSDATE=267
    SYSTEM_USER=268
    TAN=269
    THEN_SYM=270
    TIMEDIFF=271
    TIMESTAMP=272
    TIMESTAMPADD=273
    TIMESTAMPDIFF=274
    TIME_FORMAT=275
    TIME_SYM=276
    TIME_TO_SEC=277
    TIS620=278
    TO_BASE64=279
    TO_DAYS=280
    TO_SECONDS=281
    TRIM=282
    TRUE_SYM=283
    TRUNCATE=284
    UCS2=285
    UJIS=286
    UNHEX=287
    UNION_SYM=288
    UNIX_TIMESTAMP=289
    UNSIGNED_SYM=290
    UPDATE=291
    UPPER=292
    USE=293
    USER=294
    USE_SYM=295
    USING_SYM=296
    UTC_DATE=297
    UTC_TIME=298
    UTC_TIMESTAMP=299
    UTF8=300
    UUID=301
    VALUES=302
    VARIANCE=303
    VAR_POP=304
    VAR_SAMP=305
    VERSION_SYM=306
    WEEK=307
    WEEKDAY=308
    WEEKOFYEAR=309
    WEIGHT_STRING=310
    WHEN_SYM=311
    WHERE=312
    WITH=313
    XOR=314
    YEAR=315
    YEARWEEK=316
    YEAR_MONTH=317
    SDIST=318
    SAREA=319
    SCENTER=320
    SCIRCUM=321
    SLENGTH=322
    SSWAP=323
    SNPOINTS=324
    SSTR=325
    MYSQL_SPHERE_VERSION=326
    SRCONTAINSL=327
    SLCONTAINSR=328
    SRNOTCONTAINSL=329
    SLNOTCONTAINSR=330
    SOVERLAPS=331
    SNOTOVERLAPS=332
    SEQUAL=333
    SNOTEQUAL=334
    STRANSFORM=335
    SINVERSE=336
    SPOINT=337
    SPOINT_LONG=338
    SPOINT_LAT=339
    SPOINT_X=340
    SPOINT_Y=341
    SPOINT_Z=342
    SPOINT_EQUAL=343
    STRANS=344
    STRANS_POINT=345
    STRANS_POINT_INVERSE=346
    STRANS_EQUAL=347
    STRANS_EQUAL_NEG=348
    STRANS_PHI=349
    STRANS_THETA=350
    STRANS_PSI=351
    STRANS_AXES=352
    STRANS_INVERT=353
    STRANS_ZXZ=354
    STRANS_TRANS=355
    STRANS_TRANS_INV=356
    SCIRCLE=357
    SCIRCLE_RADIUS=358
    SCIRCLE_EQUAL=359
    SCIRCLE_EQUAL_NEG=360
    SCIRCLE_OVERLAP=361
    SCIRCLE_OVERLAP_NEG=362
    SCIRCLE_CONTAINED_BY_CIRCLE=363
    SCIRCLE_CONTAINED_BY_CIRCLE_NEG=364
    SCIRCLE_CONTAINS_CIRCLE=365
    SCIRCLE_CONTAINS_CIRCLE_NEG=366
    SPOINT_CONTAINED_BY_CIRCLE=367
    SPOINT_CONTAINED_BY_CIRCLE_NEG=368
    SPOINT_CONTAINED_BY_CIRCLE_COM=369
    SPOINT_CONTAINED_BY_CIRCLE_COM_NEG=370
    STRANS_CIRCLE=371
    STRANS_CIRCLE_INVERSE=372
    SLINE=373
    SMERIDIAN=374
    SLINE_BEG=375
    SLINE_END=376
    SLINE_EQUAL=377
    SLINE_EQUAL_NEG=378
    SLINE_TURN=379
    SLINE_CROSSES=380
    SLINE_CROSSES_NEG=381
    SLINE_OVERLAP=382
    SLINE_CONTAINS_POINT=383
    SLINE_CONTAINS_POINT_COM=384
    SLINE_CONTAINS_POINT_NEG=385
    SLINE_CONTAINS_POINT_COM_NEG=386
    STRANS_LINE=387
    STRANS_LINE_INVERSE=388
    SLINE_OVERLAP_CIRCLE=389
    SLINE_OVERLAP_CIRCLE_COM=390
    SLINE_OVERLAP_CIRCLE_NEG=391
    SLINE_OVERLAP_CIRCLE_COM_NEG=392
    SCIRCLE_CONTAINS_LINE=393
    SCIRCLE_CONTAINS_LINE_COM=394
    SCIRCLE_CONTAINS_LINE_NEG=395
    SCIRCLE_CONTAINS_LINE_COM_NEG=396
    SELLIPSE=397
    SELLIPSE_INC=398
    SELLIPSE_LRAD=399
    SELLIPSE_SRAD=400
    SELLIPSE_EQUAL=401
    SELLIPSE_EQUAL_NEG=402
    SELLIPSE_CONTAINS_ELLIPSE=403
    SELLIPSE_CONTAINS_ELLIPSE_NEG=404
    SELLIPSE_CONTAINS_ELLIPSE_COM=405
    SELLIPSE_CONTAINS_ELLIPSE_COM_NEG=406
    SELLIPSE_OVERLAP_ELLIPSE=407
    SELLIPSE_OVERLAP_ELLIPSE_NEG=408
    SELLIPSE_CONTAINS_POINT=409
    SELLIPSE_CONTAINS_POINT_NEG=410
    SELLIPSE_CONTAINS_POINT_COM=411
    SELLIPSE_CONTAINS_POINT_COM_NEG=412
    SELLIPSE_CONTAINS_CIRCLE=413
    SELLIPSE_CONTAINS_CIRCLE_NEG=414
    SELLIPSE_CONTAINS_CIRCLE_COM=415
    SELLIPSE_CONTAINS_CIRCLE_COM_NEG=416
    SCIRCLE_CONTAINS_ELLIPSE=417
    SCIRCLE_CONTAINS_ELLIPSE_NEG=418
    SCIRCLE_CONTAINS_ELLIPSE_COM=419
    SCIRCLE_CONTAINS_ELLIPSE_COM_NEG=420
    SELLIPSE_OVERLAP_CIRCLE=421
    SELLIPSE_OVERLAP_CIRCLE_NEG=422
    SELLIPSE_OVERLAP_CIRCLE_COM=423
    SELLIPSE_OVERLAP_CIRCLE_COM_NEG=424
    SELLIPSE_OVERLAP_LINE=425
    SELLIPSE_OVERLAP_LINE_NEG=426
    SELLIPSE_OVERLAP_LINE_COM=427
    SELLIPSE_OVERLAP_LINE_COM_NEG=428
    SELLIPSE_CONTAINS_LINE=429
    SELLIPSE_CONTAINS_LINE_NEG=430
    SELLIPSE_CONTAINS_LINE_COM=431
    SELLIPSE_CONTAINS_LINE_COM_NEG=432
    STRANS_ELLIPSE=433
    STRANS_ELLIPSE_INVERSE=434
    SPOLY=435
    SPOLY_EQUAL=436
    SPOLY_EQUAL_NEG=437
    SPOLY_CONTAINS_POLYGON=438
    SPOLY_CONTAINS_POLYGON_NEG=439
    SPOLY_CONTAINS_POLYGON_COM=440
    SPOLY_CONTAINS_POLYGON_COM_NEG=441
    SPOLY_OVERLAP_POLYGON=442
    SPOLY_OVERLAP_POLYGON_NEG=443
    SPOLY_CONTAINS_POINT=444
    SPOLY_CONTAINS_POINT_NEG=445
    SPOLY_CONTAINS_POINT_COM=446
    SPOLY_CONTAINS_POINT_COM_NEG=447
    SPOLY_CONTAINS_CIRCLE=448
    SPOLY_CONTAINS_CIRCLE_NEG=449
    SPOLY_CONTAINS_CIRCLE_COM=450
    SPOLY_CONTAINS_CIRCLE_COM_NEG=451
    SCIRCLE_CONTAINS_POLYGON=452
    SCIRCLE_CONTAINS_POLYGON_NEG=453
    SCIRCLE_CONTAINS_POLYGON_COM=454
    SCIRCLE_CONTAINS_POLYGON_COM_NEG=455
    SPOLY_OVERLAP_CIRCLE=456
    SPOLY_OVERLAP_CIRCLE_NEG=457
    SPOLY_OVERLAP_CIRCLE_COM=458
    SPOLY_OVERLAP_CIRCLE_COM_NEG=459
    SPOLY_CONTAINS_LINE=460
    SPOLY_CONTAINS_LINE_NEG=461
    SPOLY_CONTAINS_LINE_COM=462
    SPOLY_CONTAINS_LINE_COM_NEG=463
    SPOLY_OVERLAP_LINE=464
    SPOLY_OVERLAP_LINE_NEG=465
    SPOLY_OVERLAP_LINE_COM=466
    SPOLY_OVERLAP_LINE_COM_NEG=467
    SPOLY_CONTAINS_ELLIPSE=468
    SPOLY_CONTAINS_ELLIPSE_NEG=469
    SPOLY_CONTAINS_ELLIPSE_COM=470
    SPOLY_CONTAINS_ELLIPSE_COM_NEG=471
    SELLIPSE_CONTAINS_POLYGON=472
    SELLIPSE_CONTAINS_POLYGON_NEG=473
    SELLIPSE_CONTAINS_POLYGON_COM=474
    SELLIPSE_CONTAINS_POLYGON_COM_NEG=475
    SPOLY_OVERLAP_ELLIPSE=476
    SPOLY_OVERLAP_ELLIPSE_NEG=477
    SPOLY_OVERLAP_ELLIPSE_COM=478
    SPOLY_OVERLAP_ELLIPSE_COM_NEG=479
    STRANS_POLY=480
    STRANS_POLY_INVERSE=481
    SPOLY_ADD_POINT_AGGR=482
    SPOLY_AGGR=483
    SPATH=484
    SPATH_EQUAL=485
    SPATH_EQUAL_NEG=486
    SPATH_OVERLAP_PATH=487
    SPATH_OVERLAP_PATH_NEG=488
    SPATH_CONTAINS_POINT=489
    SPATH_CONTAINS_POINT_NEG=490
    SPATH_CONTAINS_POINT_COM=491
    SPATH_CONTAINS_POINT_COM_NEG=492
    SCIRCLE_CONTAINS_PATH=493
    SCIRCLE_CONTAINS_PATH_NEG=494
    SCIRCLE_CONTAINS_PATH_COM=495
    SCIRCLE_CONTAINS_PATH_COM_NEG=496
    SCIRCLE_OVERLAP_PATH=497
    SCIRCLE_OVERLAP_PATH_NEG=498
    SCIRCLE_OVERLAP_PATH_COM=499
    SCIRCLE_OVERLAP_PATH_COM_NEG=500
    SPATH_OVERLAP_LINE=501
    SPATH_OVERLAP_LINE_NEG=502
    SPATH_OVERLAP_LINE_COM=503
    SPATH_OVERLAP_LINE_COM_NEG=504
    SELLIPSE_CONTAINS_PATH=505
    SELLIPSE_CONTAINS_PATH_NEG=506
    SELLIPSE_CONTAINS_PATH_COM=507
    SELLIPSE_CONTAINS_PATH_COM_NEG=508
    SELLIPSE_OVERLAP_PATH=509
    SELLIPSE_OVERLAP_PATH_NEG=510
    SELLIPSE_OVERLAP_PATH_COM=511
    SELLIPSE_OVERLAP_PATH_COM_NEG=512
    SPOLY_CONTAINS_PATH=513
    SPOLY_CONTAINS_PATH_NEG=514
    SPOLY_CONTAINS_PATH_COM=515
    SPOLY_CONTAINS_PATH_COM_NEG=516
    SPOLY_OVERLAP_PATH=517
    SPOLY_OVERLAP_PATH_NEG=518
    SPOLY_OVERLAP_PATH_COM=519
    SPOLY_OVERLAP_PATH_COM_NEG=520
    STRANS_PATH=521
    STRANS_PATH_INVERSE=522
    SPATH_ADD_POINT_AGGR=523
    SPATH_AGGR=524
    SBOX=525
    SBOX_SW=526
    SBOX_SE=527
    SBOX_NW=528
    SBOX_NE=529
    SBOX_EQUAL=530
    SBOX_EQUAL_NEG=531
    SBOX_CONTAINS_BOX=532
    SBOX_CONTAINS_BOX_NEG=533
    SBOX_CONTAINS_BOX_COM=534
    SBOX_CONTAINS_BOX_COM_NEG=535
    SBOX_OVERLAP_BOX=536
    SBOX_OVERLAP_BOX_NEG=537
    SBOX_CONTAINS_POINT=538
    SBOX_CONTAINS_POINT_NEG=539
    SBOX_CONTAINS_POINT_COM=540
    SBOX_CONTAINS_POINT_COM_NEG=541
    SBOX_CONTAINS_CIRCLE=542
    SBOX_CONTAINS_CIRCLE_NEG=543
    SBOX_CONTAINS_CIRCLE_COM=544
    SBOX_CONTAINS_CIRCLE_COM_NEG=545
    SCIRCLE_CONTAINS_BOX=546
    SCIRCLE_CONTAINS_BOX_NEG=547
    SCIRCLE_CONTAINS_BOX_COM=548
    SCIRCLE_CONTAINS_BOX_COM_NEG=549
    SBOX_OVERLAP_CIRCLE=550
    SBOX_OVERLAP_CIRCLE_NEG=551
    SBOX_OVERLAP_CIRCLE_COM=552
    SBOX_OVERLAP_CIRCLE_COM_NEG=553
    SBOX_CONTAINS_LINE=554
    SBOX_CONTAINS_LINE_NEG=555
    SBOX_CONTAINS_LINE_COM=556
    SBOX_CONTAINS_LINE_COM_NEG=557
    SBOX_OVERLAP_LINE=558
    SBOX_OVERLAP_LINE_NEG=559
    SBOX_OVERLAP_LINE_COM=560
    SBOX_OVERLAP_LINE_COM_NEG=561
    SBOX_CONTAINS_ELLIPSE=562
    SBOX_CONTAINS_ELLIPSE_NEG=563
    SBOX_CONTAINS_ELLIPSE_COM=564
    SBOX_CONTAINS_ELLIPSE_COM_NEG=565
    SELLIPSE_CONTAINS_BOX=566
    SELLIPSE_CONTAINS_BOX_NEG=567
    SELLIPSE_CONTAINS_BOX_COM=568
    SELLIPSE_CONTAINS_BOX_COM_NEG=569
    SBOX_OVERLAP_ELLIPSE=570
    SBOX_OVERLAP_ELLIPSE_NEG=571
    SBOX_OVERLAP_ELLIPSE_COM=572
    SBOX_OVERLAP_ELLIPSE_COM_NEG=573
    SBOX_CONTAINS_POLY=574
    SBOX_CONTAINS_POLY_NEG=575
    SBOX_CONTAINS_POLY_COM=576
    SBOX_CONTAINS_POLY_COM_NEG=577
    SPOLY_CONTAINS_BOX=578
    SPOLY_CONTAINS_BOX_NEG=579
    SPOLY_CONTAINS_BOX_COM=580
    SPOLY_CONTAINS_BOX_COM_NEG=581
    SBOX_OVERLAP_POLY=582
    SBOX_OVERLAP_POLY_NEG=583
    SBOX_OVERLAP_POLY_COM=584
    SBOX_OVERLAP_POLY_COM_NEG=585
    SBOX_CONTAINS_PATH=586
    SBOX_CONTAINS_PATH_NEG=587
    SBOX_CONTAINS_PATH_COM=588
    SBOX_CONTAINS_PATH_COM_NEG=589
    SBOX_OVERLAP_PATH=590
    SBOX_OVERLAP_PATH_NEG=591
    SBOX_OVERLAP_PATH_COM=592
    SBOX_OVERLAP_PATH_COM_NEG=593
    STRRPOS=594
    IDLE=595
    ANGDIST=596
    HILBERTKEY=597
    COORDFROMHILBERTKEY=598
    SUM_OF_SQUARES=599
    PARTITADD_SUM_OF_SQARES=600
    GAIA_HEALPIX=601
    SPRNG_DBL=602
    DIVIDE=603
    MOD_SYM=604
    OR_SYM=605
    AND_SYM=606
    ARROW=607
    EQ=608
    NOT_EQ=609
    LET=610
    GET=611
    SET_VAR=612
    SHIFT_LEFT=613
    SHIFT_RIGHT=614
    SEMI=615
    COLON=616
    DOT=617
    COMMA=618
    ASTERISK=619
    RPAREN=620
    LPAREN=621
    RBRACK=622
    LBRACK=623
    PLUS=624
    MINUS=625
    NEGATION=626
    VERTBAR=627
    BITAND=628
    POWER_OP=629
    BACKTICK=630
    GTH=631
    LTH=632
    INTEGER_NUM=633
    HEX_DIGIT=634
    BIT_NUM=635
    REAL_NUMBER=636
    TEXT_STRING=637
    ID=638
    COMMENT=639
    WS=640
    USER_VAR=641

    def __init__(self, input, output=sys.stdout):
        super(MySQLParser, self).__init__(input, output=output)
        self.checkVersion("4.7")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class Relational_opContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Relational_opContext, self).__init__(parent, invokingState)
            self.parser = parser

        def EQ(self):
            return self.getToken(MySQLParser.EQ, 0)

        def LTH(self):
            return self.getToken(MySQLParser.LTH, 0)

        def GTH(self):
            return self.getToken(MySQLParser.GTH, 0)

        def NOT_EQ(self):
            return self.getToken(MySQLParser.NOT_EQ, 0)

        def LET(self):
            return self.getToken(MySQLParser.LET, 0)

        def GET(self):
            return self.getToken(MySQLParser.GET, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_relational_op

        def enterRule(self, listener):
            if hasattr(listener, "enterRelational_op"):
                listener.enterRelational_op(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitRelational_op"):
                listener.exitRelational_op(self)




    def relational_op(self):

        localctx = MySQLParser.Relational_opContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_relational_op)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 160
            _la = self._input.LA(1)
            if not(((((_la - 608)) & ~0x3f) == 0 and ((1 << (_la - 608)) & ((1 << (MySQLParser.EQ - 608)) | (1 << (MySQLParser.NOT_EQ - 608)) | (1 << (MySQLParser.LET - 608)) | (1 << (MySQLParser.GET - 608)) | (1 << (MySQLParser.GTH - 608)) | (1 << (MySQLParser.LTH - 608)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Cast_data_typeContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Cast_data_typeContext, self).__init__(parent, invokingState)
            self.parser = parser

        def BINARY(self):
            return self.getToken(MySQLParser.BINARY, 0)

        def LPAREN(self):
            return self.getToken(MySQLParser.LPAREN, 0)

        def INTEGER_NUM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.INTEGER_NUM)
            else:
                return self.getToken(MySQLParser.INTEGER_NUM, i)

        def RPAREN(self):
            return self.getToken(MySQLParser.RPAREN, 0)

        def CHAR(self):
            return self.getToken(MySQLParser.CHAR, 0)

        def DATE_SYM(self):
            return self.getToken(MySQLParser.DATE_SYM, 0)

        def DATETIME(self):
            return self.getToken(MySQLParser.DATETIME, 0)

        def DECIMAL_SYM(self):
            return self.getToken(MySQLParser.DECIMAL_SYM, 0)

        def COMMA(self):
            return self.getToken(MySQLParser.COMMA, 0)

        def SIGNED_SYM(self):
            return self.getToken(MySQLParser.SIGNED_SYM, 0)

        def INTEGER_SYM(self):
            return self.getToken(MySQLParser.INTEGER_SYM, 0)

        def TIME_SYM(self):
            return self.getToken(MySQLParser.TIME_SYM, 0)

        def UNSIGNED_SYM(self):
            return self.getToken(MySQLParser.UNSIGNED_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_cast_data_type

        def enterRule(self, listener):
            if hasattr(listener, "enterCast_data_type"):
                listener.enterCast_data_type(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCast_data_type"):
                listener.exitCast_data_type(self)




    def cast_data_type(self):

        localctx = MySQLParser.Cast_data_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_cast_data_type)
        self._la = 0 # Token type
        try:
            self.state = 195
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [MySQLParser.BINARY]:
                self.enterOuterAlt(localctx, 1)
                self.state = 162
                self.match(MySQLParser.BINARY)
                self.state = 166
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.LPAREN:
                    self.state = 163
                    self.match(MySQLParser.LPAREN)
                    self.state = 164
                    self.match(MySQLParser.INTEGER_NUM)
                    self.state = 165
                    self.match(MySQLParser.RPAREN)


                pass
            elif token in [MySQLParser.CHAR]:
                self.enterOuterAlt(localctx, 2)
                self.state = 168
                self.match(MySQLParser.CHAR)
                self.state = 172
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.LPAREN:
                    self.state = 169
                    self.match(MySQLParser.LPAREN)
                    self.state = 170
                    self.match(MySQLParser.INTEGER_NUM)
                    self.state = 171
                    self.match(MySQLParser.RPAREN)


                pass
            elif token in [MySQLParser.DATE_SYM]:
                self.enterOuterAlt(localctx, 3)
                self.state = 174
                self.match(MySQLParser.DATE_SYM)
                pass
            elif token in [MySQLParser.DATETIME]:
                self.enterOuterAlt(localctx, 4)
                self.state = 175
                self.match(MySQLParser.DATETIME)
                pass
            elif token in [MySQLParser.DECIMAL_SYM]:
                self.enterOuterAlt(localctx, 5)
                self.state = 176
                self.match(MySQLParser.DECIMAL_SYM)
                self.state = 184
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.LPAREN:
                    self.state = 177
                    self.match(MySQLParser.LPAREN)
                    self.state = 178
                    self.match(MySQLParser.INTEGER_NUM)
                    self.state = 181
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==MySQLParser.COMMA:
                        self.state = 179
                        self.match(MySQLParser.COMMA)
                        self.state = 180
                        self.match(MySQLParser.INTEGER_NUM)


                    self.state = 183
                    self.match(MySQLParser.RPAREN)


                pass
            elif token in [MySQLParser.SIGNED_SYM]:
                self.enterOuterAlt(localctx, 6)
                self.state = 186
                self.match(MySQLParser.SIGNED_SYM)
                self.state = 188
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.INTEGER_SYM:
                    self.state = 187
                    self.match(MySQLParser.INTEGER_SYM)


                pass
            elif token in [MySQLParser.TIME_SYM]:
                self.enterOuterAlt(localctx, 7)
                self.state = 190
                self.match(MySQLParser.TIME_SYM)
                pass
            elif token in [MySQLParser.UNSIGNED_SYM]:
                self.enterOuterAlt(localctx, 8)
                self.state = 191
                self.match(MySQLParser.UNSIGNED_SYM)
                self.state = 193
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.INTEGER_SYM:
                    self.state = 192
                    self.match(MySQLParser.INTEGER_SYM)


                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Search_modifierContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Search_modifierContext, self).__init__(parent, invokingState)
            self.parser = parser

        def IN_SYM(self):
            return self.getToken(MySQLParser.IN_SYM, 0)

        def NATURAL(self):
            return self.getToken(MySQLParser.NATURAL, 0)

        def LANGUAGE(self):
            return self.getToken(MySQLParser.LANGUAGE, 0)

        def MODE_SYM(self):
            return self.getToken(MySQLParser.MODE_SYM, 0)

        def WITH(self):
            return self.getToken(MySQLParser.WITH, 0)

        def QUERY_SYM(self):
            return self.getToken(MySQLParser.QUERY_SYM, 0)

        def EXPANSION_SYM(self):
            return self.getToken(MySQLParser.EXPANSION_SYM, 0)

        def BOOLEAN_SYM(self):
            return self.getToken(MySQLParser.BOOLEAN_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_search_modifier

        def enterRule(self, listener):
            if hasattr(listener, "enterSearch_modifier"):
                listener.enterSearch_modifier(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSearch_modifier"):
                listener.exitSearch_modifier(self)




    def search_modifier(self):

        localctx = MySQLParser.Search_modifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_search_modifier)
        try:
            self.state = 212
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 197
                self.match(MySQLParser.IN_SYM)
                self.state = 198
                self.match(MySQLParser.NATURAL)
                self.state = 199
                self.match(MySQLParser.LANGUAGE)
                self.state = 200
                self.match(MySQLParser.MODE_SYM)
                self.state = 204
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
                if la_ == 1:
                    self.state = 201
                    self.match(MySQLParser.WITH)
                    self.state = 202
                    self.match(MySQLParser.QUERY_SYM)
                    self.state = 203
                    self.match(MySQLParser.EXPANSION_SYM)


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 206
                self.match(MySQLParser.IN_SYM)
                self.state = 207
                self.match(MySQLParser.BOOLEAN_SYM)
                self.state = 208
                self.match(MySQLParser.MODE_SYM)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 209
                self.match(MySQLParser.WITH)
                self.state = 210
                self.match(MySQLParser.QUERY_SYM)
                self.state = 211
                self.match(MySQLParser.EXPANSION_SYM)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Interval_unitContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Interval_unitContext, self).__init__(parent, invokingState)
            self.parser = parser

        def SECOND(self):
            return self.getToken(MySQLParser.SECOND, 0)

        def MINUTE(self):
            return self.getToken(MySQLParser.MINUTE, 0)

        def HOUR(self):
            return self.getToken(MySQLParser.HOUR, 0)

        def DAY_SYM(self):
            return self.getToken(MySQLParser.DAY_SYM, 0)

        def WEEK(self):
            return self.getToken(MySQLParser.WEEK, 0)

        def MONTH(self):
            return self.getToken(MySQLParser.MONTH, 0)

        def QUARTER(self):
            return self.getToken(MySQLParser.QUARTER, 0)

        def YEAR(self):
            return self.getToken(MySQLParser.YEAR, 0)

        def SECOND_MICROSECOND(self):
            return self.getToken(MySQLParser.SECOND_MICROSECOND, 0)

        def MINUTE_MICROSECOND(self):
            return self.getToken(MySQLParser.MINUTE_MICROSECOND, 0)

        def MINUTE_SECOND(self):
            return self.getToken(MySQLParser.MINUTE_SECOND, 0)

        def HOUR_MICROSECOND(self):
            return self.getToken(MySQLParser.HOUR_MICROSECOND, 0)

        def HOUR_SECOND(self):
            return self.getToken(MySQLParser.HOUR_SECOND, 0)

        def HOUR_MINUTE(self):
            return self.getToken(MySQLParser.HOUR_MINUTE, 0)

        def DAY_MICROSECOND(self):
            return self.getToken(MySQLParser.DAY_MICROSECOND, 0)

        def DAY_SECOND(self):
            return self.getToken(MySQLParser.DAY_SECOND, 0)

        def DAY_MINUTE(self):
            return self.getToken(MySQLParser.DAY_MINUTE, 0)

        def DAY_HOUR(self):
            return self.getToken(MySQLParser.DAY_HOUR, 0)

        def YEAR_MONTH(self):
            return self.getToken(MySQLParser.YEAR_MONTH, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_interval_unit

        def enterRule(self, listener):
            if hasattr(listener, "enterInterval_unit"):
                listener.enterInterval_unit(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitInterval_unit"):
                listener.exitInterval_unit(self)




    def interval_unit(self):

        localctx = MySQLParser.Interval_unitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_interval_unit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 214
            _la = self._input.LA(1)
            if not(((((_la - 75)) & ~0x3f) == 0 and ((1 << (_la - 75)) & ((1 << (MySQLParser.DAY_HOUR - 75)) | (1 << (MySQLParser.DAY_MICROSECOND - 75)) | (1 << (MySQLParser.DAY_MINUTE - 75)) | (1 << (MySQLParser.DAY_SECOND - 75)) | (1 << (MySQLParser.DAY_SYM - 75)) | (1 << (MySQLParser.HOUR - 75)) | (1 << (MySQLParser.HOUR_MICROSECOND - 75)) | (1 << (MySQLParser.HOUR_MINUTE - 75)) | (1 << (MySQLParser.HOUR_SECOND - 75)))) != 0) or ((((_la - 187)) & ~0x3f) == 0 and ((1 << (_la - 187)) & ((1 << (MySQLParser.MINUTE - 187)) | (1 << (MySQLParser.MINUTE_MICROSECOND - 187)) | (1 << (MySQLParser.MINUTE_SECOND - 187)) | (1 << (MySQLParser.MONTH - 187)) | (1 << (MySQLParser.QUARTER - 187)) | (1 << (MySQLParser.SECOND - 187)) | (1 << (MySQLParser.SECOND_MICROSECOND - 187)))) != 0) or ((((_la - 307)) & ~0x3f) == 0 and ((1 << (_la - 307)) & ((1 << (MySQLParser.WEEK - 307)) | (1 << (MySQLParser.YEAR - 307)) | (1 << (MySQLParser.YEAR_MONTH - 307)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Transcoding_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Transcoding_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LATIN1(self):
            return self.getToken(MySQLParser.LATIN1, 0)

        def UTF8(self):
            return self.getToken(MySQLParser.UTF8, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_transcoding_name

        def enterRule(self, listener):
            if hasattr(listener, "enterTranscoding_name"):
                listener.enterTranscoding_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTranscoding_name"):
                listener.exitTranscoding_name(self)




    def transcoding_name(self):

        localctx = MySQLParser.Transcoding_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_transcoding_name)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 216
            _la = self._input.LA(1)
            if not(_la==MySQLParser.LATIN1 or _la==MySQLParser.UTF8):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Bit_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Bit_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def BIT_NUM(self):
            return self.getToken(MySQLParser.BIT_NUM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_bit_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterBit_literal"):
                listener.enterBit_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBit_literal"):
                listener.exitBit_literal(self)




    def bit_literal(self):

        localctx = MySQLParser.Bit_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_bit_literal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 218
            self.match(MySQLParser.BIT_NUM)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Boolean_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Boolean_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def TRUE_SYM(self):
            return self.getToken(MySQLParser.TRUE_SYM, 0)

        def FALSE_SYM(self):
            return self.getToken(MySQLParser.FALSE_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_boolean_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterBoolean_literal"):
                listener.enterBoolean_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBoolean_literal"):
                listener.exitBoolean_literal(self)




    def boolean_literal(self):

        localctx = MySQLParser.Boolean_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_boolean_literal)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 220
            _la = self._input.LA(1)
            if not(_la==MySQLParser.FALSE_SYM or _la==MySQLParser.TRUE_SYM):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Hex_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Hex_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def HEX_DIGIT(self):
            return self.getToken(MySQLParser.HEX_DIGIT, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_hex_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterHex_literal"):
                listener.enterHex_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitHex_literal"):
                listener.exitHex_literal(self)




    def hex_literal(self):

        localctx = MySQLParser.Hex_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_hex_literal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 222
            self.match(MySQLParser.HEX_DIGIT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Number_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Number_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def INTEGER_NUM(self):
            return self.getToken(MySQLParser.INTEGER_NUM, 0)

        def REAL_NUMBER(self):
            return self.getToken(MySQLParser.REAL_NUMBER, 0)

        def PLUS(self):
            return self.getToken(MySQLParser.PLUS, 0)

        def MINUS(self):
            return self.getToken(MySQLParser.MINUS, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_number_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterNumber_literal"):
                listener.enterNumber_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNumber_literal"):
                listener.exitNumber_literal(self)




    def number_literal(self):

        localctx = MySQLParser.Number_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_number_literal)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 225
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.PLUS or _la==MySQLParser.MINUS:
                self.state = 224
                _la = self._input.LA(1)
                if not(_la==MySQLParser.PLUS or _la==MySQLParser.MINUS):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


            self.state = 227
            _la = self._input.LA(1)
            if not(_la==MySQLParser.INTEGER_NUM or _la==MySQLParser.REAL_NUMBER):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class String_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.String_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def TEXT_STRING(self):
            return self.getToken(MySQLParser.TEXT_STRING, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_string_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterString_literal"):
                listener.enterString_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitString_literal"):
                listener.exitString_literal(self)




    def string_literal(self):

        localctx = MySQLParser.String_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_string_literal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 229
            self.match(MySQLParser.TEXT_STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Char_functionsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Char_functionsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ASCII_SYM(self):
            return self.getToken(MySQLParser.ASCII_SYM, 0)

        def BIN(self):
            return self.getToken(MySQLParser.BIN, 0)

        def BIT_LENGTH(self):
            return self.getToken(MySQLParser.BIT_LENGTH, 0)

        def CHAR_LENGTH(self):
            return self.getToken(MySQLParser.CHAR_LENGTH, 0)

        def CHAR(self):
            return self.getToken(MySQLParser.CHAR, 0)

        def CONCAT_WS(self):
            return self.getToken(MySQLParser.CONCAT_WS, 0)

        def CONCAT(self):
            return self.getToken(MySQLParser.CONCAT, 0)

        def ELT(self):
            return self.getToken(MySQLParser.ELT, 0)

        def EXPORT_SET(self):
            return self.getToken(MySQLParser.EXPORT_SET, 0)

        def FIELD(self):
            return self.getToken(MySQLParser.FIELD, 0)

        def FIND_IN_SET(self):
            return self.getToken(MySQLParser.FIND_IN_SET, 0)

        def FORMAT(self):
            return self.getToken(MySQLParser.FORMAT, 0)

        def FROM_BASE64(self):
            return self.getToken(MySQLParser.FROM_BASE64, 0)

        def HEX(self):
            return self.getToken(MySQLParser.HEX, 0)

        def INSERT(self):
            return self.getToken(MySQLParser.INSERT, 0)

        def INSTR(self):
            return self.getToken(MySQLParser.INSTR, 0)

        def LEFT(self):
            return self.getToken(MySQLParser.LEFT, 0)

        def LENGTH(self):
            return self.getToken(MySQLParser.LENGTH, 0)

        def LOAD_FILE(self):
            return self.getToken(MySQLParser.LOAD_FILE, 0)

        def LOCATE(self):
            return self.getToken(MySQLParser.LOCATE, 0)

        def LOWER(self):
            return self.getToken(MySQLParser.LOWER, 0)

        def LPAD(self):
            return self.getToken(MySQLParser.LPAD, 0)

        def LTRIM(self):
            return self.getToken(MySQLParser.LTRIM, 0)

        def MAKE_SET(self):
            return self.getToken(MySQLParser.MAKE_SET, 0)

        def MID(self):
            return self.getToken(MySQLParser.MID, 0)

        def OCT(self):
            return self.getToken(MySQLParser.OCT, 0)

        def ORD(self):
            return self.getToken(MySQLParser.ORD, 0)

        def QUOTE(self):
            return self.getToken(MySQLParser.QUOTE, 0)

        def REPEAT(self):
            return self.getToken(MySQLParser.REPEAT, 0)

        def REPLACE(self):
            return self.getToken(MySQLParser.REPLACE, 0)

        def REVERSE(self):
            return self.getToken(MySQLParser.REVERSE, 0)

        def RIGHT(self):
            return self.getToken(MySQLParser.RIGHT, 0)

        def RPAD(self):
            return self.getToken(MySQLParser.RPAD, 0)

        def RTRIM(self):
            return self.getToken(MySQLParser.RTRIM, 0)

        def SOUNDEX(self):
            return self.getToken(MySQLParser.SOUNDEX, 0)

        def SPACE(self):
            return self.getToken(MySQLParser.SPACE, 0)

        def STRCMP(self):
            return self.getToken(MySQLParser.STRCMP, 0)

        def SUBSTRING_INDEX(self):
            return self.getToken(MySQLParser.SUBSTRING_INDEX, 0)

        def SUBSTRING(self):
            return self.getToken(MySQLParser.SUBSTRING, 0)

        def TO_BASE64(self):
            return self.getToken(MySQLParser.TO_BASE64, 0)

        def TRIM(self):
            return self.getToken(MySQLParser.TRIM, 0)

        def UNHEX(self):
            return self.getToken(MySQLParser.UNHEX, 0)

        def UPPER(self):
            return self.getToken(MySQLParser.UPPER, 0)

        def WEIGHT_STRING(self):
            return self.getToken(MySQLParser.WEIGHT_STRING, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_char_functions

        def enterRule(self, listener):
            if hasattr(listener, "enterChar_functions"):
                listener.enterChar_functions(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitChar_functions"):
                listener.exitChar_functions(self)




    def char_functions(self):

        localctx = MySQLParser.Char_functionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_char_functions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 231
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << MySQLParser.ASCII_SYM) | (1 << MySQLParser.BIN) | (1 << MySQLParser.BIT_LENGTH) | (1 << MySQLParser.CHAR) | (1 << MySQLParser.CHAR_LENGTH) | (1 << MySQLParser.CONCAT) | (1 << MySQLParser.CONCAT_WS))) != 0) or ((((_la - 91)) & ~0x3f) == 0 and ((1 << (_la - 91)) & ((1 << (MySQLParser.ELT - 91)) | (1 << (MySQLParser.EXPORT_SET - 91)) | (1 << (MySQLParser.FIELD - 91)) | (1 << (MySQLParser.FIND_IN_SET - 91)) | (1 << (MySQLParser.FORMAT - 91)) | (1 << (MySQLParser.FROM_BASE64 - 91)) | (1 << (MySQLParser.HEX - 91)) | (1 << (MySQLParser.INSERT - 91)) | (1 << (MySQLParser.INSTR - 91)))) != 0) or ((((_la - 161)) & ~0x3f) == 0 and ((1 << (_la - 161)) & ((1 << (MySQLParser.LEFT - 161)) | (1 << (MySQLParser.LENGTH - 161)) | (1 << (MySQLParser.LOAD_FILE - 161)) | (1 << (MySQLParser.LOCATE - 161)) | (1 << (MySQLParser.LOWER - 161)) | (1 << (MySQLParser.LPAD - 161)) | (1 << (MySQLParser.LTRIM - 161)) | (1 << (MySQLParser.MAKE_SET - 161)) | (1 << (MySQLParser.MID - 161)) | (1 << (MySQLParser.OCT - 161)) | (1 << (MySQLParser.ORD - 161)) | (1 << (MySQLParser.QUOTE - 161)) | (1 << (MySQLParser.REPEAT - 161)) | (1 << (MySQLParser.REPLACE - 161)))) != 0) or ((((_la - 225)) & ~0x3f) == 0 and ((1 << (_la - 225)) & ((1 << (MySQLParser.REVERSE - 225)) | (1 << (MySQLParser.RIGHT - 225)) | (1 << (MySQLParser.RPAD - 225)) | (1 << (MySQLParser.RTRIM - 225)) | (1 << (MySQLParser.SOUNDEX - 225)) | (1 << (MySQLParser.SPACE - 225)) | (1 << (MySQLParser.STRCMP - 225)) | (1 << (MySQLParser.SUBSTRING - 225)) | (1 << (MySQLParser.SUBSTRING_INDEX - 225)) | (1 << (MySQLParser.TO_BASE64 - 225)) | (1 << (MySQLParser.TRIM - 225)) | (1 << (MySQLParser.UNHEX - 225)))) != 0) or _la==MySQLParser.UPPER or _la==MySQLParser.WEIGHT_STRING):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Group_functionsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Group_functionsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def AVG(self):
            return self.getToken(MySQLParser.AVG, 0)

        def COUNT(self):
            return self.getToken(MySQLParser.COUNT, 0)

        def MAX_SYM(self):
            return self.getToken(MySQLParser.MAX_SYM, 0)

        def MIN_SYM(self):
            return self.getToken(MySQLParser.MIN_SYM, 0)

        def SUM(self):
            return self.getToken(MySQLParser.SUM, 0)

        def BIT_AND(self):
            return self.getToken(MySQLParser.BIT_AND, 0)

        def BIT_OR(self):
            return self.getToken(MySQLParser.BIT_OR, 0)

        def BIT_XOR(self):
            return self.getToken(MySQLParser.BIT_XOR, 0)

        def BIT_COUNT(self):
            return self.getToken(MySQLParser.BIT_COUNT, 0)

        def GROUP_CONCAT(self):
            return self.getToken(MySQLParser.GROUP_CONCAT, 0)

        def STD(self):
            return self.getToken(MySQLParser.STD, 0)

        def STDDEV(self):
            return self.getToken(MySQLParser.STDDEV, 0)

        def STDDEV_POP(self):
            return self.getToken(MySQLParser.STDDEV_POP, 0)

        def STDDEV_SAMP(self):
            return self.getToken(MySQLParser.STDDEV_SAMP, 0)

        def VAR_POP(self):
            return self.getToken(MySQLParser.VAR_POP, 0)

        def VAR_SAMP(self):
            return self.getToken(MySQLParser.VAR_SAMP, 0)

        def VARIANCE(self):
            return self.getToken(MySQLParser.VARIANCE, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_group_functions

        def enterRule(self, listener):
            if hasattr(listener, "enterGroup_functions"):
                listener.enterGroup_functions(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitGroup_functions"):
                listener.exitGroup_functions(self)




    def group_functions(self):

        localctx = MySQLParser.Group_functionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_group_functions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 233
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << MySQLParser.AVG) | (1 << MySQLParser.BIT_AND) | (1 << MySQLParser.BIT_COUNT) | (1 << MySQLParser.BIT_OR) | (1 << MySQLParser.BIT_XOR) | (1 << MySQLParser.COUNT))) != 0) or _la==MySQLParser.GROUP_CONCAT or _la==MySQLParser.MAX_SYM or _la==MySQLParser.MIN_SYM or ((((_la - 255)) & ~0x3f) == 0 and ((1 << (_la - 255)) & ((1 << (MySQLParser.STD - 255)) | (1 << (MySQLParser.STDDEV - 255)) | (1 << (MySQLParser.STDDEV_POP - 255)) | (1 << (MySQLParser.STDDEV_SAMP - 255)) | (1 << (MySQLParser.SUM - 255)) | (1 << (MySQLParser.VARIANCE - 255)) | (1 << (MySQLParser.VAR_POP - 255)) | (1 << (MySQLParser.VAR_SAMP - 255)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Number_functionsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Number_functionsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ABS(self):
            return self.getToken(MySQLParser.ABS, 0)

        def ACOS(self):
            return self.getToken(MySQLParser.ACOS, 0)

        def ASIN(self):
            return self.getToken(MySQLParser.ASIN, 0)

        def ATAN2(self):
            return self.getToken(MySQLParser.ATAN2, 0)

        def ATAN(self):
            return self.getToken(MySQLParser.ATAN, 0)

        def CEIL(self):
            return self.getToken(MySQLParser.CEIL, 0)

        def CEILING(self):
            return self.getToken(MySQLParser.CEILING, 0)

        def CONV(self):
            return self.getToken(MySQLParser.CONV, 0)

        def COS(self):
            return self.getToken(MySQLParser.COS, 0)

        def COT(self):
            return self.getToken(MySQLParser.COT, 0)

        def CRC32(self):
            return self.getToken(MySQLParser.CRC32, 0)

        def DEGREES(self):
            return self.getToken(MySQLParser.DEGREES, 0)

        def EXP(self):
            return self.getToken(MySQLParser.EXP, 0)

        def FLOOR(self):
            return self.getToken(MySQLParser.FLOOR, 0)

        def LN(self):
            return self.getToken(MySQLParser.LN, 0)

        def LOG10(self):
            return self.getToken(MySQLParser.LOG10, 0)

        def LOG2(self):
            return self.getToken(MySQLParser.LOG2, 0)

        def LOG(self):
            return self.getToken(MySQLParser.LOG, 0)

        def MOD(self):
            return self.getToken(MySQLParser.MOD, 0)

        def PI(self):
            return self.getToken(MySQLParser.PI, 0)

        def POW(self):
            return self.getToken(MySQLParser.POW, 0)

        def POWER(self):
            return self.getToken(MySQLParser.POWER, 0)

        def RADIANS(self):
            return self.getToken(MySQLParser.RADIANS, 0)

        def RAND(self):
            return self.getToken(MySQLParser.RAND, 0)

        def ROUND(self):
            return self.getToken(MySQLParser.ROUND, 0)

        def SIGN(self):
            return self.getToken(MySQLParser.SIGN, 0)

        def SIN(self):
            return self.getToken(MySQLParser.SIN, 0)

        def SQRT(self):
            return self.getToken(MySQLParser.SQRT, 0)

        def TAN(self):
            return self.getToken(MySQLParser.TAN, 0)

        def TRUNCATE(self):
            return self.getToken(MySQLParser.TRUNCATE, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_number_functions

        def enterRule(self, listener):
            if hasattr(listener, "enterNumber_functions"):
                listener.enterNumber_functions(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNumber_functions"):
                listener.exitNumber_functions(self)




    def number_functions(self):

        localctx = MySQLParser.Number_functionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_number_functions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 235
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << MySQLParser.ABS) | (1 << MySQLParser.ACOS) | (1 << MySQLParser.ASIN) | (1 << MySQLParser.ATAN) | (1 << MySQLParser.ATAN2) | (1 << MySQLParser.CEIL) | (1 << MySQLParser.CEILING) | (1 << MySQLParser.CONV) | (1 << MySQLParser.COS) | (1 << MySQLParser.COT) | (1 << MySQLParser.CRC32))) != 0) or ((((_la - 84)) & ~0x3f) == 0 and ((1 << (_la - 84)) & ((1 << (MySQLParser.DEGREES - 84)) | (1 << (MySQLParser.EXP - 84)) | (1 << (MySQLParser.FLOOR - 84)))) != 0) or ((((_la - 165)) & ~0x3f) == 0 and ((1 << (_la - 165)) & ((1 << (MySQLParser.LN - 165)) | (1 << (MySQLParser.LOG - 165)) | (1 << (MySQLParser.LOG10 - 165)) | (1 << (MySQLParser.LOG2 - 165)) | (1 << (MySQLParser.MOD - 165)) | (1 << (MySQLParser.PI - 165)) | (1 << (MySQLParser.POW - 165)) | (1 << (MySQLParser.POWER - 165)) | (1 << (MySQLParser.RADIANS - 165)) | (1 << (MySQLParser.RAND - 165)) | (1 << (MySQLParser.ROUND - 165)))) != 0) or ((((_la - 240)) & ~0x3f) == 0 and ((1 << (_la - 240)) & ((1 << (MySQLParser.SIGN - 240)) | (1 << (MySQLParser.SIN - 240)) | (1 << (MySQLParser.SQRT - 240)) | (1 << (MySQLParser.TAN - 240)) | (1 << (MySQLParser.TRUNCATE - 240)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Other_functionsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Other_functionsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def MAKE_SET(self):
            return self.getToken(MySQLParser.MAKE_SET, 0)

        def LOAD_FILE(self):
            return self.getToken(MySQLParser.LOAD_FILE, 0)

        def IF(self):
            return self.getToken(MySQLParser.IF, 0)

        def IFNULL(self):
            return self.getToken(MySQLParser.IFNULL, 0)

        def AES_ENCRYPT(self):
            return self.getToken(MySQLParser.AES_ENCRYPT, 0)

        def AES_DECRYPT(self):
            return self.getToken(MySQLParser.AES_DECRYPT, 0)

        def DECODE(self):
            return self.getToken(MySQLParser.DECODE, 0)

        def ENCODE(self):
            return self.getToken(MySQLParser.ENCODE, 0)

        def DES_DECRYPT(self):
            return self.getToken(MySQLParser.DES_DECRYPT, 0)

        def DES_ENCRYPT(self):
            return self.getToken(MySQLParser.DES_ENCRYPT, 0)

        def ENCRYPT(self):
            return self.getToken(MySQLParser.ENCRYPT, 0)

        def MD5(self):
            return self.getToken(MySQLParser.MD5, 0)

        def OLD_PASSWORD(self):
            return self.getToken(MySQLParser.OLD_PASSWORD, 0)

        def PASSWORD(self):
            return self.getToken(MySQLParser.PASSWORD, 0)

        def BENCHMARK(self):
            return self.getToken(MySQLParser.BENCHMARK, 0)

        def CHARSET(self):
            return self.getToken(MySQLParser.CHARSET, 0)

        def COERCIBILITY(self):
            return self.getToken(MySQLParser.COERCIBILITY, 0)

        def COLLATION(self):
            return self.getToken(MySQLParser.COLLATION, 0)

        def CONNECTION_ID(self):
            return self.getToken(MySQLParser.CONNECTION_ID, 0)

        def CURRENT_USER(self):
            return self.getToken(MySQLParser.CURRENT_USER, 0)

        def DATABASE(self):
            return self.getToken(MySQLParser.DATABASE, 0)

        def SCHEMA(self):
            return self.getToken(MySQLParser.SCHEMA, 0)

        def USER(self):
            return self.getToken(MySQLParser.USER, 0)

        def SESSION_USER(self):
            return self.getToken(MySQLParser.SESSION_USER, 0)

        def SYSTEM_USER(self):
            return self.getToken(MySQLParser.SYSTEM_USER, 0)

        def VERSION_SYM(self):
            return self.getToken(MySQLParser.VERSION_SYM, 0)

        def FOUND_ROWS(self):
            return self.getToken(MySQLParser.FOUND_ROWS, 0)

        def LAST_INSERT_ID(self):
            return self.getToken(MySQLParser.LAST_INSERT_ID, 0)

        def DEFAULT(self):
            return self.getToken(MySQLParser.DEFAULT, 0)

        def GET_LOCK(self):
            return self.getToken(MySQLParser.GET_LOCK, 0)

        def RELEASE_LOCK(self):
            return self.getToken(MySQLParser.RELEASE_LOCK, 0)

        def IS_FREE_LOCK(self):
            return self.getToken(MySQLParser.IS_FREE_LOCK, 0)

        def IS_USED_LOCK(self):
            return self.getToken(MySQLParser.IS_USED_LOCK, 0)

        def MASTER_POS_WAIT(self):
            return self.getToken(MySQLParser.MASTER_POS_WAIT, 0)

        def INET_ATON(self):
            return self.getToken(MySQLParser.INET_ATON, 0)

        def INET_NTOA(self):
            return self.getToken(MySQLParser.INET_NTOA, 0)

        def NAME_CONST(self):
            return self.getToken(MySQLParser.NAME_CONST, 0)

        def SLEEP(self):
            return self.getToken(MySQLParser.SLEEP, 0)

        def UUID(self):
            return self.getToken(MySQLParser.UUID, 0)

        def VALUES(self):
            return self.getToken(MySQLParser.VALUES, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_other_functions

        def enterRule(self, listener):
            if hasattr(listener, "enterOther_functions"):
                listener.enterOther_functions(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOther_functions"):
                listener.exitOther_functions(self)




    def other_functions(self):

        localctx = MySQLParser.Other_functionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_other_functions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 237
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << MySQLParser.AES_DECRYPT) | (1 << MySQLParser.AES_ENCRYPT) | (1 << MySQLParser.BENCHMARK) | (1 << MySQLParser.CHARSET) | (1 << MySQLParser.COERCIBILITY) | (1 << MySQLParser.COLLATION) | (1 << MySQLParser.CONNECTION_ID) | (1 << MySQLParser.CURRENT_USER))) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & ((1 << (MySQLParser.DATABASE - 64)) | (1 << (MySQLParser.DECODE - 64)) | (1 << (MySQLParser.DEFAULT - 64)) | (1 << (MySQLParser.DES_DECRYPT - 64)) | (1 << (MySQLParser.DES_ENCRYPT - 64)) | (1 << (MySQLParser.ENCODE - 64)) | (1 << (MySQLParser.ENCRYPT - 64)) | (1 << (MySQLParser.FOUND_ROWS - 64)) | (1 << (MySQLParser.GET_LOCK - 64)))) != 0) or ((((_la - 132)) & ~0x3f) == 0 and ((1 << (_la - 132)) & ((1 << (MySQLParser.IF - 132)) | (1 << (MySQLParser.IFNULL - 132)) | (1 << (MySQLParser.INET_ATON - 132)) | (1 << (MySQLParser.INET_NTOA - 132)) | (1 << (MySQLParser.IS_FREE_LOCK - 132)) | (1 << (MySQLParser.IS_USED_LOCK - 132)) | (1 << (MySQLParser.LAST_INSERT_ID - 132)) | (1 << (MySQLParser.LOAD_FILE - 132)) | (1 << (MySQLParser.MAKE_SET - 132)) | (1 << (MySQLParser.MASTER_POS_WAIT - 132)) | (1 << (MySQLParser.MD5 - 132)) | (1 << (MySQLParser.NAME_CONST - 132)))) != 0) or ((((_la - 203)) & ~0x3f) == 0 and ((1 << (_la - 203)) & ((1 << (MySQLParser.OLD_PASSWORD - 203)) | (1 << (MySQLParser.PASSWORD - 203)) | (1 << (MySQLParser.RELEASE_LOCK - 203)) | (1 << (MySQLParser.SCHEMA - 203)) | (1 << (MySQLParser.SESSION_USER - 203)) | (1 << (MySQLParser.SLEEP - 203)))) != 0) or ((((_la - 268)) & ~0x3f) == 0 and ((1 << (_la - 268)) & ((1 << (MySQLParser.SYSTEM_USER - 268)) | (1 << (MySQLParser.USER - 268)) | (1 << (MySQLParser.UUID - 268)) | (1 << (MySQLParser.VALUES - 268)) | (1 << (MySQLParser.VERSION_SYM - 268)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Time_functionsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Time_functionsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ADDDATE(self):
            return self.getToken(MySQLParser.ADDDATE, 0)

        def ADDTIME(self):
            return self.getToken(MySQLParser.ADDTIME, 0)

        def CONVERT_TZ(self):
            return self.getToken(MySQLParser.CONVERT_TZ, 0)

        def CURDATE(self):
            return self.getToken(MySQLParser.CURDATE, 0)

        def CURTIME(self):
            return self.getToken(MySQLParser.CURTIME, 0)

        def DATE_ADD(self):
            return self.getToken(MySQLParser.DATE_ADD, 0)

        def DATE_FORMAT(self):
            return self.getToken(MySQLParser.DATE_FORMAT, 0)

        def DATE_SUB(self):
            return self.getToken(MySQLParser.DATE_SUB, 0)

        def DATE_SYM(self):
            return self.getToken(MySQLParser.DATE_SYM, 0)

        def DATEDIFF(self):
            return self.getToken(MySQLParser.DATEDIFF, 0)

        def DAYNAME(self):
            return self.getToken(MySQLParser.DAYNAME, 0)

        def DAYOFMONTH(self):
            return self.getToken(MySQLParser.DAYOFMONTH, 0)

        def DAYOFWEEK(self):
            return self.getToken(MySQLParser.DAYOFWEEK, 0)

        def DAYOFYEAR(self):
            return self.getToken(MySQLParser.DAYOFYEAR, 0)

        def EXTRACT(self):
            return self.getToken(MySQLParser.EXTRACT, 0)

        def FROM_DAYS(self):
            return self.getToken(MySQLParser.FROM_DAYS, 0)

        def FROM_UNIXTIME(self):
            return self.getToken(MySQLParser.FROM_UNIXTIME, 0)

        def GET_FORMAT(self):
            return self.getToken(MySQLParser.GET_FORMAT, 0)

        def HOUR(self):
            return self.getToken(MySQLParser.HOUR, 0)

        def LAST_DAY(self):
            return self.getToken(MySQLParser.LAST_DAY, 0)

        def MAKEDATE(self):
            return self.getToken(MySQLParser.MAKEDATE, 0)

        def MAKETIME(self):
            return self.getToken(MySQLParser.MAKETIME, 0)

        def MICROSECOND(self):
            return self.getToken(MySQLParser.MICROSECOND, 0)

        def MINUTE(self):
            return self.getToken(MySQLParser.MINUTE, 0)

        def MONTH(self):
            return self.getToken(MySQLParser.MONTH, 0)

        def MONTHNAME(self):
            return self.getToken(MySQLParser.MONTHNAME, 0)

        def NOW(self):
            return self.getToken(MySQLParser.NOW, 0)

        def PERIOD_ADD(self):
            return self.getToken(MySQLParser.PERIOD_ADD, 0)

        def PERIOD_DIFF(self):
            return self.getToken(MySQLParser.PERIOD_DIFF, 0)

        def QUARTER(self):
            return self.getToken(MySQLParser.QUARTER, 0)

        def SEC_TO_TIME(self):
            return self.getToken(MySQLParser.SEC_TO_TIME, 0)

        def SECOND(self):
            return self.getToken(MySQLParser.SECOND, 0)

        def STR_TO_DATE(self):
            return self.getToken(MySQLParser.STR_TO_DATE, 0)

        def SUBTIME(self):
            return self.getToken(MySQLParser.SUBTIME, 0)

        def SYSDATE(self):
            return self.getToken(MySQLParser.SYSDATE, 0)

        def TIME_FORMAT(self):
            return self.getToken(MySQLParser.TIME_FORMAT, 0)

        def TIME_TO_SEC(self):
            return self.getToken(MySQLParser.TIME_TO_SEC, 0)

        def TIME_SYM(self):
            return self.getToken(MySQLParser.TIME_SYM, 0)

        def TIMEDIFF(self):
            return self.getToken(MySQLParser.TIMEDIFF, 0)

        def TIMESTAMP(self):
            return self.getToken(MySQLParser.TIMESTAMP, 0)

        def TIMESTAMPADD(self):
            return self.getToken(MySQLParser.TIMESTAMPADD, 0)

        def TIMESTAMPDIFF(self):
            return self.getToken(MySQLParser.TIMESTAMPDIFF, 0)

        def TO_DAYS(self):
            return self.getToken(MySQLParser.TO_DAYS, 0)

        def TO_SECONDS(self):
            return self.getToken(MySQLParser.TO_SECONDS, 0)

        def UNIX_TIMESTAMP(self):
            return self.getToken(MySQLParser.UNIX_TIMESTAMP, 0)

        def UTC_DATE(self):
            return self.getToken(MySQLParser.UTC_DATE, 0)

        def UTC_TIME(self):
            return self.getToken(MySQLParser.UTC_TIME, 0)

        def UTC_TIMESTAMP(self):
            return self.getToken(MySQLParser.UTC_TIMESTAMP, 0)

        def WEEK(self):
            return self.getToken(MySQLParser.WEEK, 0)

        def WEEKDAY(self):
            return self.getToken(MySQLParser.WEEKDAY, 0)

        def WEEKOFYEAR(self):
            return self.getToken(MySQLParser.WEEKOFYEAR, 0)

        def YEAR(self):
            return self.getToken(MySQLParser.YEAR, 0)

        def YEARWEEK(self):
            return self.getToken(MySQLParser.YEARWEEK, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_time_functions

        def enterRule(self, listener):
            if hasattr(listener, "enterTime_functions"):
                listener.enterTime_functions(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTime_functions"):
                listener.exitTime_functions(self)




    def time_functions(self):

        localctx = MySQLParser.Time_functionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_time_functions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 239
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << MySQLParser.ADDDATE) | (1 << MySQLParser.ADDTIME) | (1 << MySQLParser.CONVERT_TZ) | (1 << MySQLParser.CURDATE) | (1 << MySQLParser.CURTIME))) != 0) or ((((_la - 65)) & ~0x3f) == 0 and ((1 << (_la - 65)) & ((1 << (MySQLParser.DATEDIFF - 65)) | (1 << (MySQLParser.DATE_ADD - 65)) | (1 << (MySQLParser.DATE_FORMAT - 65)) | (1 << (MySQLParser.DATE_SUB - 65)) | (1 << (MySQLParser.DATE_SYM - 65)) | (1 << (MySQLParser.DAYNAME - 65)) | (1 << (MySQLParser.DAYOFMONTH - 65)) | (1 << (MySQLParser.DAYOFWEEK - 65)) | (1 << (MySQLParser.DAYOFYEAR - 65)) | (1 << (MySQLParser.EXTRACT - 65)) | (1 << (MySQLParser.FROM_DAYS - 65)) | (1 << (MySQLParser.FROM_UNIXTIME - 65)) | (1 << (MySQLParser.GET_FORMAT - 65)) | (1 << (MySQLParser.HOUR - 65)))) != 0) or ((((_la - 153)) & ~0x3f) == 0 and ((1 << (_la - 153)) & ((1 << (MySQLParser.LAST_DAY - 153)) | (1 << (MySQLParser.MAKEDATE - 153)) | (1 << (MySQLParser.MAKETIME - 153)) | (1 << (MySQLParser.MICROSECOND - 153)) | (1 << (MySQLParser.MINUTE - 153)) | (1 << (MySQLParser.MONTH - 153)) | (1 << (MySQLParser.MONTHNAME - 153)) | (1 << (MySQLParser.NOW - 153)) | (1 << (MySQLParser.PERIOD_ADD - 153)) | (1 << (MySQLParser.PERIOD_DIFF - 153)) | (1 << (MySQLParser.QUARTER - 153)))) != 0) or ((((_la - 233)) & ~0x3f) == 0 and ((1 << (_la - 233)) & ((1 << (MySQLParser.SECOND - 233)) | (1 << (MySQLParser.SEC_TO_TIME - 233)) | (1 << (MySQLParser.STR_TO_DATE - 233)) | (1 << (MySQLParser.SUBTIME - 233)) | (1 << (MySQLParser.SYSDATE - 233)) | (1 << (MySQLParser.TIMEDIFF - 233)) | (1 << (MySQLParser.TIMESTAMP - 233)) | (1 << (MySQLParser.TIMESTAMPADD - 233)) | (1 << (MySQLParser.TIMESTAMPDIFF - 233)) | (1 << (MySQLParser.TIME_FORMAT - 233)) | (1 << (MySQLParser.TIME_SYM - 233)) | (1 << (MySQLParser.TIME_TO_SEC - 233)) | (1 << (MySQLParser.TO_DAYS - 233)) | (1 << (MySQLParser.TO_SECONDS - 233)) | (1 << (MySQLParser.UNIX_TIMESTAMP - 233)))) != 0) or ((((_la - 297)) & ~0x3f) == 0 and ((1 << (_la - 297)) & ((1 << (MySQLParser.UTC_DATE - 297)) | (1 << (MySQLParser.UTC_TIME - 297)) | (1 << (MySQLParser.UTC_TIMESTAMP - 297)) | (1 << (MySQLParser.WEEK - 297)) | (1 << (MySQLParser.WEEKDAY - 297)) | (1 << (MySQLParser.WEEKOFYEAR - 297)) | (1 << (MySQLParser.YEAR - 297)) | (1 << (MySQLParser.YEARWEEK - 297)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Mysql_sphere_functionsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Mysql_sphere_functionsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def SDIST(self):
            return self.getToken(MySQLParser.SDIST, 0)

        def SAREA(self):
            return self.getToken(MySQLParser.SAREA, 0)

        def SCENTER(self):
            return self.getToken(MySQLParser.SCENTER, 0)

        def SCIRCUM(self):
            return self.getToken(MySQLParser.SCIRCUM, 0)

        def SLENGTH(self):
            return self.getToken(MySQLParser.SLENGTH, 0)

        def SSWAP(self):
            return self.getToken(MySQLParser.SSWAP, 0)

        def SNPOINTS(self):
            return self.getToken(MySQLParser.SNPOINTS, 0)

        def SSTR(self):
            return self.getToken(MySQLParser.SSTR, 0)

        def MYSQL_SPHERE_VERSION(self):
            return self.getToken(MySQLParser.MYSQL_SPHERE_VERSION, 0)

        def SRCONTAINSL(self):
            return self.getToken(MySQLParser.SRCONTAINSL, 0)

        def SLCONTAINSR(self):
            return self.getToken(MySQLParser.SLCONTAINSR, 0)

        def SRNOTCONTAINSL(self):
            return self.getToken(MySQLParser.SRNOTCONTAINSL, 0)

        def SLNOTCONTAINSR(self):
            return self.getToken(MySQLParser.SLNOTCONTAINSR, 0)

        def SOVERLAPS(self):
            return self.getToken(MySQLParser.SOVERLAPS, 0)

        def SNOTOVERLAPS(self):
            return self.getToken(MySQLParser.SNOTOVERLAPS, 0)

        def SEQUAL(self):
            return self.getToken(MySQLParser.SEQUAL, 0)

        def SNOTEQUAL(self):
            return self.getToken(MySQLParser.SNOTEQUAL, 0)

        def STRANSFORM(self):
            return self.getToken(MySQLParser.STRANSFORM, 0)

        def SINVERSE(self):
            return self.getToken(MySQLParser.SINVERSE, 0)

        def SPOINT(self):
            return self.getToken(MySQLParser.SPOINT, 0)

        def SPOINT_LONG(self):
            return self.getToken(MySQLParser.SPOINT_LONG, 0)

        def SPOINT_LAT(self):
            return self.getToken(MySQLParser.SPOINT_LAT, 0)

        def SPOINT_X(self):
            return self.getToken(MySQLParser.SPOINT_X, 0)

        def SPOINT_Y(self):
            return self.getToken(MySQLParser.SPOINT_Y, 0)

        def SPOINT_Z(self):
            return self.getToken(MySQLParser.SPOINT_Z, 0)

        def SPOINT_EQUAL(self):
            return self.getToken(MySQLParser.SPOINT_EQUAL, 0)

        def STRANS(self):
            return self.getToken(MySQLParser.STRANS, 0)

        def STRANS_POINT(self):
            return self.getToken(MySQLParser.STRANS_POINT, 0)

        def STRANS_POINT_INVERSE(self):
            return self.getToken(MySQLParser.STRANS_POINT_INVERSE, 0)

        def STRANS_EQUAL(self):
            return self.getToken(MySQLParser.STRANS_EQUAL, 0)

        def STRANS_EQUAL_NEG(self):
            return self.getToken(MySQLParser.STRANS_EQUAL_NEG, 0)

        def STRANS_PHI(self):
            return self.getToken(MySQLParser.STRANS_PHI, 0)

        def STRANS_THETA(self):
            return self.getToken(MySQLParser.STRANS_THETA, 0)

        def STRANS_PSI(self):
            return self.getToken(MySQLParser.STRANS_PSI, 0)

        def STRANS_AXES(self):
            return self.getToken(MySQLParser.STRANS_AXES, 0)

        def STRANS_INVERT(self):
            return self.getToken(MySQLParser.STRANS_INVERT, 0)

        def STRANS_ZXZ(self):
            return self.getToken(MySQLParser.STRANS_ZXZ, 0)

        def STRANS_TRANS(self):
            return self.getToken(MySQLParser.STRANS_TRANS, 0)

        def STRANS_TRANS_INV(self):
            return self.getToken(MySQLParser.STRANS_TRANS_INV, 0)

        def SCIRCLE(self):
            return self.getToken(MySQLParser.SCIRCLE, 0)

        def SCIRCLE_RADIUS(self):
            return self.getToken(MySQLParser.SCIRCLE_RADIUS, 0)

        def SCIRCLE_EQUAL(self):
            return self.getToken(MySQLParser.SCIRCLE_EQUAL, 0)

        def SCIRCLE_EQUAL_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_EQUAL_NEG, 0)

        def SCIRCLE_OVERLAP(self):
            return self.getToken(MySQLParser.SCIRCLE_OVERLAP, 0)

        def SCIRCLE_OVERLAP_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_OVERLAP_NEG, 0)

        def SCIRCLE_CONTAINED_BY_CIRCLE(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE, 0)

        def SCIRCLE_CONTAINED_BY_CIRCLE_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE_NEG, 0)

        def SCIRCLE_CONTAINS_CIRCLE(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_CIRCLE, 0)

        def SCIRCLE_CONTAINS_CIRCLE_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_CIRCLE_NEG, 0)

        def SPOINT_CONTAINED_BY_CIRCLE(self):
            return self.getToken(MySQLParser.SPOINT_CONTAINED_BY_CIRCLE, 0)

        def SPOINT_CONTAINED_BY_CIRCLE_NEG(self):
            return self.getToken(MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_NEG, 0)

        def SPOINT_CONTAINED_BY_CIRCLE_COM(self):
            return self.getToken(MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM, 0)

        def SPOINT_CONTAINED_BY_CIRCLE_COM_NEG(self):
            return self.getToken(MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM_NEG, 0)

        def STRANS_CIRCLE(self):
            return self.getToken(MySQLParser.STRANS_CIRCLE, 0)

        def STRANS_CIRCLE_INVERSE(self):
            return self.getToken(MySQLParser.STRANS_CIRCLE_INVERSE, 0)

        def SLINE(self):
            return self.getToken(MySQLParser.SLINE, 0)

        def SMERIDIAN(self):
            return self.getToken(MySQLParser.SMERIDIAN, 0)

        def SLINE_BEG(self):
            return self.getToken(MySQLParser.SLINE_BEG, 0)

        def SLINE_END(self):
            return self.getToken(MySQLParser.SLINE_END, 0)

        def SLINE_EQUAL(self):
            return self.getToken(MySQLParser.SLINE_EQUAL, 0)

        def SLINE_EQUAL_NEG(self):
            return self.getToken(MySQLParser.SLINE_EQUAL_NEG, 0)

        def SLINE_TURN(self):
            return self.getToken(MySQLParser.SLINE_TURN, 0)

        def SLINE_CROSSES(self):
            return self.getToken(MySQLParser.SLINE_CROSSES, 0)

        def SLINE_CROSSES_NEG(self):
            return self.getToken(MySQLParser.SLINE_CROSSES_NEG, 0)

        def SLINE_OVERLAP(self):
            return self.getToken(MySQLParser.SLINE_OVERLAP, 0)

        def SLINE_CONTAINS_POINT(self):
            return self.getToken(MySQLParser.SLINE_CONTAINS_POINT, 0)

        def SLINE_CONTAINS_POINT_COM(self):
            return self.getToken(MySQLParser.SLINE_CONTAINS_POINT_COM, 0)

        def SLINE_CONTAINS_POINT_NEG(self):
            return self.getToken(MySQLParser.SLINE_CONTAINS_POINT_NEG, 0)

        def SLINE_CONTAINS_POINT_COM_NEG(self):
            return self.getToken(MySQLParser.SLINE_CONTAINS_POINT_COM_NEG, 0)

        def STRANS_LINE(self):
            return self.getToken(MySQLParser.STRANS_LINE, 0)

        def STRANS_LINE_INVERSE(self):
            return self.getToken(MySQLParser.STRANS_LINE_INVERSE, 0)

        def SLINE_OVERLAP_CIRCLE(self):
            return self.getToken(MySQLParser.SLINE_OVERLAP_CIRCLE, 0)

        def SLINE_OVERLAP_CIRCLE_COM(self):
            return self.getToken(MySQLParser.SLINE_OVERLAP_CIRCLE_COM, 0)

        def SLINE_OVERLAP_CIRCLE_NEG(self):
            return self.getToken(MySQLParser.SLINE_OVERLAP_CIRCLE_NEG, 0)

        def SLINE_OVERLAP_CIRCLE_COM_NEG(self):
            return self.getToken(MySQLParser.SLINE_OVERLAP_CIRCLE_COM_NEG, 0)

        def SCIRCLE_CONTAINS_LINE(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_LINE, 0)

        def SCIRCLE_CONTAINS_LINE_COM(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_LINE_COM, 0)

        def SCIRCLE_CONTAINS_LINE_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_LINE_NEG, 0)

        def SCIRCLE_CONTAINS_LINE_COM_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_LINE_COM_NEG, 0)

        def SELLIPSE(self):
            return self.getToken(MySQLParser.SELLIPSE, 0)

        def SELLIPSE_INC(self):
            return self.getToken(MySQLParser.SELLIPSE_INC, 0)

        def SELLIPSE_LRAD(self):
            return self.getToken(MySQLParser.SELLIPSE_LRAD, 0)

        def SELLIPSE_SRAD(self):
            return self.getToken(MySQLParser.SELLIPSE_SRAD, 0)

        def SELLIPSE_EQUAL(self):
            return self.getToken(MySQLParser.SELLIPSE_EQUAL, 0)

        def SELLIPSE_EQUAL_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_EQUAL_NEG, 0)

        def SELLIPSE_CONTAINS_ELLIPSE(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_ELLIPSE, 0)

        def SELLIPSE_CONTAINS_ELLIPSE_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_NEG, 0)

        def SELLIPSE_CONTAINS_ELLIPSE_COM(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM, 0)

        def SELLIPSE_CONTAINS_ELLIPSE_COM_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM_NEG, 0)

        def SELLIPSE_OVERLAP_ELLIPSE(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_ELLIPSE, 0)

        def SELLIPSE_OVERLAP_ELLIPSE_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_ELLIPSE_NEG, 0)

        def SELLIPSE_CONTAINS_POINT(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_POINT, 0)

        def SELLIPSE_CONTAINS_POINT_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_POINT_NEG, 0)

        def SELLIPSE_CONTAINS_POINT_COM(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_POINT_COM, 0)

        def SELLIPSE_CONTAINS_POINT_COM_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_POINT_COM_NEG, 0)

        def SELLIPSE_CONTAINS_CIRCLE(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_CIRCLE, 0)

        def SELLIPSE_CONTAINS_CIRCLE_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_CIRCLE_NEG, 0)

        def SELLIPSE_CONTAINS_CIRCLE_COM(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM, 0)

        def SELLIPSE_CONTAINS_CIRCLE_COM_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM_NEG, 0)

        def SCIRCLE_CONTAINS_ELLIPSE(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_ELLIPSE, 0)

        def SCIRCLE_CONTAINS_ELLIPSE_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_NEG, 0)

        def SCIRCLE_CONTAINS_ELLIPSE_COM(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM, 0)

        def SCIRCLE_CONTAINS_ELLIPSE_COM_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM_NEG, 0)

        def SELLIPSE_OVERLAP_CIRCLE(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_CIRCLE, 0)

        def SELLIPSE_OVERLAP_CIRCLE_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_CIRCLE_NEG, 0)

        def SELLIPSE_OVERLAP_CIRCLE_COM(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM, 0)

        def SELLIPSE_OVERLAP_CIRCLE_COM_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM_NEG, 0)

        def SELLIPSE_OVERLAP_LINE(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_LINE, 0)

        def SELLIPSE_OVERLAP_LINE_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_LINE_NEG, 0)

        def SELLIPSE_OVERLAP_LINE_COM(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_LINE_COM, 0)

        def SELLIPSE_OVERLAP_LINE_COM_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_LINE_COM_NEG, 0)

        def SELLIPSE_CONTAINS_LINE(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_LINE, 0)

        def SELLIPSE_CONTAINS_LINE_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_LINE_NEG, 0)

        def SELLIPSE_CONTAINS_LINE_COM(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_LINE_COM, 0)

        def SELLIPSE_CONTAINS_LINE_COM_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_LINE_COM_NEG, 0)

        def STRANS_ELLIPSE(self):
            return self.getToken(MySQLParser.STRANS_ELLIPSE, 0)

        def STRANS_ELLIPSE_INVERSE(self):
            return self.getToken(MySQLParser.STRANS_ELLIPSE_INVERSE, 0)

        def SPOLY(self):
            return self.getToken(MySQLParser.SPOLY, 0)

        def SPOLY_EQUAL(self):
            return self.getToken(MySQLParser.SPOLY_EQUAL, 0)

        def SPOLY_EQUAL_NEG(self):
            return self.getToken(MySQLParser.SPOLY_EQUAL_NEG, 0)

        def SPOLY_CONTAINS_POLYGON(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_POLYGON, 0)

        def SPOLY_CONTAINS_POLYGON_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_POLYGON_NEG, 0)

        def SPOLY_CONTAINS_POLYGON_COM(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_POLYGON_COM, 0)

        def SPOLY_CONTAINS_POLYGON_COM_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_POLYGON_COM_NEG, 0)

        def SPOLY_OVERLAP_POLYGON(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_POLYGON, 0)

        def SPOLY_OVERLAP_POLYGON_NEG(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_POLYGON_NEG, 0)

        def SPOLY_CONTAINS_POINT(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_POINT, 0)

        def SPOLY_CONTAINS_POINT_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_POINT_NEG, 0)

        def SPOLY_CONTAINS_POINT_COM(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_POINT_COM, 0)

        def SPOLY_CONTAINS_POINT_COM_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_POINT_COM_NEG, 0)

        def SPOLY_CONTAINS_CIRCLE(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_CIRCLE, 0)

        def SPOLY_CONTAINS_CIRCLE_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_CIRCLE_NEG, 0)

        def SPOLY_CONTAINS_CIRCLE_COM(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_CIRCLE_COM, 0)

        def SPOLY_CONTAINS_CIRCLE_COM_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_CIRCLE_COM_NEG, 0)

        def SCIRCLE_CONTAINS_POLYGON(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_POLYGON, 0)

        def SCIRCLE_CONTAINS_POLYGON_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_POLYGON_NEG, 0)

        def SCIRCLE_CONTAINS_POLYGON_COM(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM, 0)

        def SCIRCLE_CONTAINS_POLYGON_COM_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM_NEG, 0)

        def SPOLY_OVERLAP_CIRCLE(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_CIRCLE, 0)

        def SPOLY_OVERLAP_CIRCLE_NEG(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_CIRCLE_NEG, 0)

        def SPOLY_OVERLAP_CIRCLE_COM(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_CIRCLE_COM, 0)

        def SPOLY_OVERLAP_CIRCLE_COM_NEG(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_CIRCLE_COM_NEG, 0)

        def SPOLY_CONTAINS_LINE(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_LINE, 0)

        def SPOLY_CONTAINS_LINE_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_LINE_NEG, 0)

        def SPOLY_CONTAINS_LINE_COM(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_LINE_COM, 0)

        def SPOLY_CONTAINS_LINE_COM_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_LINE_COM_NEG, 0)

        def SPOLY_OVERLAP_LINE(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_LINE, 0)

        def SPOLY_OVERLAP_LINE_NEG(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_LINE_NEG, 0)

        def SPOLY_OVERLAP_LINE_COM(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_LINE_COM, 0)

        def SPOLY_OVERLAP_LINE_COM_NEG(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_LINE_COM_NEG, 0)

        def SPOLY_CONTAINS_ELLIPSE(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_ELLIPSE, 0)

        def SPOLY_CONTAINS_ELLIPSE_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_ELLIPSE_NEG, 0)

        def SPOLY_CONTAINS_ELLIPSE_COM(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM, 0)

        def SPOLY_CONTAINS_ELLIPSE_COM_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM_NEG, 0)

        def SELLIPSE_CONTAINS_POLYGON(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_POLYGON, 0)

        def SELLIPSE_CONTAINS_POLYGON_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_POLYGON_NEG, 0)

        def SELLIPSE_CONTAINS_POLYGON_COM(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM, 0)

        def SELLIPSE_CONTAINS_POLYGON_COM_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM_NEG, 0)

        def SPOLY_OVERLAP_ELLIPSE(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_ELLIPSE, 0)

        def SPOLY_OVERLAP_ELLIPSE_NEG(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_ELLIPSE_NEG, 0)

        def SPOLY_OVERLAP_ELLIPSE_COM(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM, 0)

        def SPOLY_OVERLAP_ELLIPSE_COM_NEG(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM_NEG, 0)

        def STRANS_POLY(self):
            return self.getToken(MySQLParser.STRANS_POLY, 0)

        def STRANS_POLY_INVERSE(self):
            return self.getToken(MySQLParser.STRANS_POLY_INVERSE, 0)

        def SPOLY_ADD_POINT_AGGR(self):
            return self.getToken(MySQLParser.SPOLY_ADD_POINT_AGGR, 0)

        def SPOLY_AGGR(self):
            return self.getToken(MySQLParser.SPOLY_AGGR, 0)

        def SPATH(self):
            return self.getToken(MySQLParser.SPATH, 0)

        def SPATH_EQUAL(self):
            return self.getToken(MySQLParser.SPATH_EQUAL, 0)

        def SPATH_EQUAL_NEG(self):
            return self.getToken(MySQLParser.SPATH_EQUAL_NEG, 0)

        def SPATH_OVERLAP_PATH(self):
            return self.getToken(MySQLParser.SPATH_OVERLAP_PATH, 0)

        def SPATH_OVERLAP_PATH_NEG(self):
            return self.getToken(MySQLParser.SPATH_OVERLAP_PATH_NEG, 0)

        def SPATH_CONTAINS_POINT(self):
            return self.getToken(MySQLParser.SPATH_CONTAINS_POINT, 0)

        def SPATH_CONTAINS_POINT_NEG(self):
            return self.getToken(MySQLParser.SPATH_CONTAINS_POINT_NEG, 0)

        def SPATH_CONTAINS_POINT_COM(self):
            return self.getToken(MySQLParser.SPATH_CONTAINS_POINT_COM, 0)

        def SPATH_CONTAINS_POINT_COM_NEG(self):
            return self.getToken(MySQLParser.SPATH_CONTAINS_POINT_COM_NEG, 0)

        def SCIRCLE_CONTAINS_PATH(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_PATH, 0)

        def SCIRCLE_CONTAINS_PATH_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_PATH_NEG, 0)

        def SCIRCLE_CONTAINS_PATH_COM(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_PATH_COM, 0)

        def SCIRCLE_CONTAINS_PATH_COM_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_PATH_COM_NEG, 0)

        def SCIRCLE_OVERLAP_PATH(self):
            return self.getToken(MySQLParser.SCIRCLE_OVERLAP_PATH, 0)

        def SCIRCLE_OVERLAP_PATH_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_OVERLAP_PATH_NEG, 0)

        def SCIRCLE_OVERLAP_PATH_COM(self):
            return self.getToken(MySQLParser.SCIRCLE_OVERLAP_PATH_COM, 0)

        def SCIRCLE_OVERLAP_PATH_COM_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_OVERLAP_PATH_COM_NEG, 0)

        def SPATH_OVERLAP_LINE(self):
            return self.getToken(MySQLParser.SPATH_OVERLAP_LINE, 0)

        def SPATH_OVERLAP_LINE_NEG(self):
            return self.getToken(MySQLParser.SPATH_OVERLAP_LINE_NEG, 0)

        def SPATH_OVERLAP_LINE_COM(self):
            return self.getToken(MySQLParser.SPATH_OVERLAP_LINE_COM, 0)

        def SPATH_OVERLAP_LINE_COM_NEG(self):
            return self.getToken(MySQLParser.SPATH_OVERLAP_LINE_COM_NEG, 0)

        def SELLIPSE_CONTAINS_PATH(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_PATH, 0)

        def SELLIPSE_CONTAINS_PATH_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_PATH_NEG, 0)

        def SELLIPSE_CONTAINS_PATH_COM(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_PATH_COM, 0)

        def SELLIPSE_CONTAINS_PATH_COM_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_PATH_COM_NEG, 0)

        def SELLIPSE_OVERLAP_PATH(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_PATH, 0)

        def SELLIPSE_OVERLAP_PATH_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_PATH_NEG, 0)

        def SELLIPSE_OVERLAP_PATH_COM(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_PATH_COM, 0)

        def SELLIPSE_OVERLAP_PATH_COM_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_OVERLAP_PATH_COM_NEG, 0)

        def SPOLY_CONTAINS_PATH(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_PATH, 0)

        def SPOLY_CONTAINS_PATH_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_PATH_NEG, 0)

        def SPOLY_CONTAINS_PATH_COM(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_PATH_COM, 0)

        def SPOLY_CONTAINS_PATH_COM_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_PATH_COM_NEG, 0)

        def SPOLY_OVERLAP_PATH(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_PATH, 0)

        def SPOLY_OVERLAP_PATH_NEG(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_PATH_NEG, 0)

        def SPOLY_OVERLAP_PATH_COM(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_PATH_COM, 0)

        def SPOLY_OVERLAP_PATH_COM_NEG(self):
            return self.getToken(MySQLParser.SPOLY_OVERLAP_PATH_COM_NEG, 0)

        def STRANS_PATH(self):
            return self.getToken(MySQLParser.STRANS_PATH, 0)

        def STRANS_PATH_INVERSE(self):
            return self.getToken(MySQLParser.STRANS_PATH_INVERSE, 0)

        def SPATH_ADD_POINT_AGGR(self):
            return self.getToken(MySQLParser.SPATH_ADD_POINT_AGGR, 0)

        def SPATH_AGGR(self):
            return self.getToken(MySQLParser.SPATH_AGGR, 0)

        def SBOX(self):
            return self.getToken(MySQLParser.SBOX, 0)

        def SBOX_SW(self):
            return self.getToken(MySQLParser.SBOX_SW, 0)

        def SBOX_SE(self):
            return self.getToken(MySQLParser.SBOX_SE, 0)

        def SBOX_NW(self):
            return self.getToken(MySQLParser.SBOX_NW, 0)

        def SBOX_NE(self):
            return self.getToken(MySQLParser.SBOX_NE, 0)

        def SBOX_EQUAL(self):
            return self.getToken(MySQLParser.SBOX_EQUAL, 0)

        def SBOX_EQUAL_NEG(self):
            return self.getToken(MySQLParser.SBOX_EQUAL_NEG, 0)

        def SBOX_CONTAINS_BOX(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_BOX, 0)

        def SBOX_CONTAINS_BOX_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_BOX_NEG, 0)

        def SBOX_CONTAINS_BOX_COM(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_BOX_COM, 0)

        def SBOX_CONTAINS_BOX_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_BOX_COM_NEG, 0)

        def SBOX_OVERLAP_BOX(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_BOX, 0)

        def SBOX_OVERLAP_BOX_NEG(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_BOX_NEG, 0)

        def SBOX_CONTAINS_POINT(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_POINT, 0)

        def SBOX_CONTAINS_POINT_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_POINT_NEG, 0)

        def SBOX_CONTAINS_POINT_COM(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_POINT_COM, 0)

        def SBOX_CONTAINS_POINT_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_POINT_COM_NEG, 0)

        def SBOX_CONTAINS_CIRCLE(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_CIRCLE, 0)

        def SBOX_CONTAINS_CIRCLE_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_CIRCLE_NEG, 0)

        def SBOX_CONTAINS_CIRCLE_COM(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_CIRCLE_COM, 0)

        def SBOX_CONTAINS_CIRCLE_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_CIRCLE_COM_NEG, 0)

        def SCIRCLE_CONTAINS_BOX(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_BOX, 0)

        def SCIRCLE_CONTAINS_BOX_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_BOX_NEG, 0)

        def SCIRCLE_CONTAINS_BOX_COM(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_BOX_COM, 0)

        def SCIRCLE_CONTAINS_BOX_COM_NEG(self):
            return self.getToken(MySQLParser.SCIRCLE_CONTAINS_BOX_COM_NEG, 0)

        def SBOX_OVERLAP_CIRCLE(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_CIRCLE, 0)

        def SBOX_OVERLAP_CIRCLE_NEG(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_CIRCLE_NEG, 0)

        def SBOX_OVERLAP_CIRCLE_COM(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_CIRCLE_COM, 0)

        def SBOX_OVERLAP_CIRCLE_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_CIRCLE_COM_NEG, 0)

        def SBOX_CONTAINS_LINE(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_LINE, 0)

        def SBOX_CONTAINS_LINE_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_LINE_NEG, 0)

        def SBOX_CONTAINS_LINE_COM(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_LINE_COM, 0)

        def SBOX_CONTAINS_LINE_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_LINE_COM_NEG, 0)

        def SBOX_OVERLAP_LINE(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_LINE, 0)

        def SBOX_OVERLAP_LINE_NEG(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_LINE_NEG, 0)

        def SBOX_OVERLAP_LINE_COM(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_LINE_COM, 0)

        def SBOX_OVERLAP_LINE_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_LINE_COM_NEG, 0)

        def SBOX_CONTAINS_ELLIPSE(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_ELLIPSE, 0)

        def SBOX_CONTAINS_ELLIPSE_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_ELLIPSE_NEG, 0)

        def SBOX_CONTAINS_ELLIPSE_COM(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_ELLIPSE_COM, 0)

        def SBOX_CONTAINS_ELLIPSE_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_ELLIPSE_COM_NEG, 0)

        def SELLIPSE_CONTAINS_BOX(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_BOX, 0)

        def SELLIPSE_CONTAINS_BOX_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_BOX_NEG, 0)

        def SELLIPSE_CONTAINS_BOX_COM(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_BOX_COM, 0)

        def SELLIPSE_CONTAINS_BOX_COM_NEG(self):
            return self.getToken(MySQLParser.SELLIPSE_CONTAINS_BOX_COM_NEG, 0)

        def SBOX_OVERLAP_ELLIPSE(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_ELLIPSE, 0)

        def SBOX_OVERLAP_ELLIPSE_NEG(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_ELLIPSE_NEG, 0)

        def SBOX_OVERLAP_ELLIPSE_COM(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_ELLIPSE_COM, 0)

        def SBOX_OVERLAP_ELLIPSE_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_ELLIPSE_COM_NEG, 0)

        def SBOX_CONTAINS_POLY(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_POLY, 0)

        def SBOX_CONTAINS_POLY_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_POLY_NEG, 0)

        def SBOX_CONTAINS_POLY_COM(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_POLY_COM, 0)

        def SBOX_CONTAINS_POLY_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_POLY_COM_NEG, 0)

        def SPOLY_CONTAINS_BOX(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_BOX, 0)

        def SPOLY_CONTAINS_BOX_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_BOX_NEG, 0)

        def SPOLY_CONTAINS_BOX_COM(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_BOX_COM, 0)

        def SPOLY_CONTAINS_BOX_COM_NEG(self):
            return self.getToken(MySQLParser.SPOLY_CONTAINS_BOX_COM_NEG, 0)

        def SBOX_OVERLAP_POLY(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_POLY, 0)

        def SBOX_OVERLAP_POLY_NEG(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_POLY_NEG, 0)

        def SBOX_OVERLAP_POLY_COM(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_POLY_COM, 0)

        def SBOX_OVERLAP_POLY_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_POLY_COM_NEG, 0)

        def SBOX_CONTAINS_PATH(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_PATH, 0)

        def SBOX_CONTAINS_PATH_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_PATH_NEG, 0)

        def SBOX_CONTAINS_PATH_COM(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_PATH_COM, 0)

        def SBOX_CONTAINS_PATH_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_CONTAINS_PATH_COM_NEG, 0)

        def SBOX_OVERLAP_PATH(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_PATH, 0)

        def SBOX_OVERLAP_PATH_NEG(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_PATH_NEG, 0)

        def SBOX_OVERLAP_PATH_COM(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_PATH_COM, 0)

        def SBOX_OVERLAP_PATH_COM_NEG(self):
            return self.getToken(MySQLParser.SBOX_OVERLAP_PATH_COM_NEG, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_mysql_sphere_functions

        def enterRule(self, listener):
            if hasattr(listener, "enterMysql_sphere_functions"):
                listener.enterMysql_sphere_functions(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMysql_sphere_functions"):
                listener.exitMysql_sphere_functions(self)




    def mysql_sphere_functions(self):

        localctx = MySQLParser.Mysql_sphere_functionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_mysql_sphere_functions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 241
            _la = self._input.LA(1)
            if not(((((_la - 318)) & ~0x3f) == 0 and ((1 << (_la - 318)) & ((1 << (MySQLParser.SDIST - 318)) | (1 << (MySQLParser.SAREA - 318)) | (1 << (MySQLParser.SCENTER - 318)) | (1 << (MySQLParser.SCIRCUM - 318)) | (1 << (MySQLParser.SLENGTH - 318)) | (1 << (MySQLParser.SSWAP - 318)) | (1 << (MySQLParser.SNPOINTS - 318)) | (1 << (MySQLParser.SSTR - 318)) | (1 << (MySQLParser.MYSQL_SPHERE_VERSION - 318)) | (1 << (MySQLParser.SRCONTAINSL - 318)) | (1 << (MySQLParser.SLCONTAINSR - 318)) | (1 << (MySQLParser.SRNOTCONTAINSL - 318)) | (1 << (MySQLParser.SLNOTCONTAINSR - 318)) | (1 << (MySQLParser.SOVERLAPS - 318)) | (1 << (MySQLParser.SNOTOVERLAPS - 318)) | (1 << (MySQLParser.SEQUAL - 318)) | (1 << (MySQLParser.SNOTEQUAL - 318)) | (1 << (MySQLParser.STRANSFORM - 318)) | (1 << (MySQLParser.SINVERSE - 318)) | (1 << (MySQLParser.SPOINT - 318)) | (1 << (MySQLParser.SPOINT_LONG - 318)) | (1 << (MySQLParser.SPOINT_LAT - 318)) | (1 << (MySQLParser.SPOINT_X - 318)) | (1 << (MySQLParser.SPOINT_Y - 318)) | (1 << (MySQLParser.SPOINT_Z - 318)) | (1 << (MySQLParser.SPOINT_EQUAL - 318)) | (1 << (MySQLParser.STRANS - 318)) | (1 << (MySQLParser.STRANS_POINT - 318)) | (1 << (MySQLParser.STRANS_POINT_INVERSE - 318)) | (1 << (MySQLParser.STRANS_EQUAL - 318)) | (1 << (MySQLParser.STRANS_EQUAL_NEG - 318)) | (1 << (MySQLParser.STRANS_PHI - 318)) | (1 << (MySQLParser.STRANS_THETA - 318)) | (1 << (MySQLParser.STRANS_PSI - 318)) | (1 << (MySQLParser.STRANS_AXES - 318)) | (1 << (MySQLParser.STRANS_INVERT - 318)) | (1 << (MySQLParser.STRANS_ZXZ - 318)) | (1 << (MySQLParser.STRANS_TRANS - 318)) | (1 << (MySQLParser.STRANS_TRANS_INV - 318)) | (1 << (MySQLParser.SCIRCLE - 318)) | (1 << (MySQLParser.SCIRCLE_RADIUS - 318)) | (1 << (MySQLParser.SCIRCLE_EQUAL - 318)) | (1 << (MySQLParser.SCIRCLE_EQUAL_NEG - 318)) | (1 << (MySQLParser.SCIRCLE_OVERLAP - 318)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_NEG - 318)) | (1 << (MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE - 318)) | (1 << (MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE_NEG - 318)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_CIRCLE - 318)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_CIRCLE_NEG - 318)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE - 318)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_NEG - 318)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM - 318)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM_NEG - 318)) | (1 << (MySQLParser.STRANS_CIRCLE - 318)) | (1 << (MySQLParser.STRANS_CIRCLE_INVERSE - 318)) | (1 << (MySQLParser.SLINE - 318)) | (1 << (MySQLParser.SMERIDIAN - 318)) | (1 << (MySQLParser.SLINE_BEG - 318)) | (1 << (MySQLParser.SLINE_END - 318)) | (1 << (MySQLParser.SLINE_EQUAL - 318)) | (1 << (MySQLParser.SLINE_EQUAL_NEG - 318)) | (1 << (MySQLParser.SLINE_TURN - 318)) | (1 << (MySQLParser.SLINE_CROSSES - 318)) | (1 << (MySQLParser.SLINE_CROSSES_NEG - 318)))) != 0) or ((((_la - 382)) & ~0x3f) == 0 and ((1 << (_la - 382)) & ((1 << (MySQLParser.SLINE_OVERLAP - 382)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT - 382)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT_COM - 382)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT_NEG - 382)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT_COM_NEG - 382)) | (1 << (MySQLParser.STRANS_LINE - 382)) | (1 << (MySQLParser.STRANS_LINE_INVERSE - 382)) | (1 << (MySQLParser.SLINE_OVERLAP_CIRCLE - 382)) | (1 << (MySQLParser.SLINE_OVERLAP_CIRCLE_COM - 382)) | (1 << (MySQLParser.SLINE_OVERLAP_CIRCLE_NEG - 382)) | (1 << (MySQLParser.SLINE_OVERLAP_CIRCLE_COM_NEG - 382)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE - 382)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE_COM - 382)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE_NEG - 382)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE_COM_NEG - 382)) | (1 << (MySQLParser.SELLIPSE - 382)) | (1 << (MySQLParser.SELLIPSE_INC - 382)) | (1 << (MySQLParser.SELLIPSE_LRAD - 382)) | (1 << (MySQLParser.SELLIPSE_SRAD - 382)) | (1 << (MySQLParser.SELLIPSE_EQUAL - 382)) | (1 << (MySQLParser.SELLIPSE_EQUAL_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_ELLIPSE - 382)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_ELLIPSE_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT_COM - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT_COM_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM_NEG - 382)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE - 382)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_NEG - 382)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM - 382)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE - 382)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM - 382)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE - 382)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE_COM - 382)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE_COM_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE_NEG - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE_COM - 382)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE_COM_NEG - 382)) | (1 << (MySQLParser.STRANS_ELLIPSE - 382)) | (1 << (MySQLParser.STRANS_ELLIPSE_INVERSE - 382)) | (1 << (MySQLParser.SPOLY - 382)) | (1 << (MySQLParser.SPOLY_EQUAL - 382)) | (1 << (MySQLParser.SPOLY_EQUAL_NEG - 382)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON - 382)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON_NEG - 382)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON_COM - 382)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON_COM_NEG - 382)) | (1 << (MySQLParser.SPOLY_OVERLAP_POLYGON - 382)) | (1 << (MySQLParser.SPOLY_OVERLAP_POLYGON_NEG - 382)) | (1 << (MySQLParser.SPOLY_CONTAINS_POINT - 382)) | (1 << (MySQLParser.SPOLY_CONTAINS_POINT_NEG - 382)))) != 0) or ((((_la - 446)) & ~0x3f) == 0 and ((1 << (_la - 446)) & ((1 << (MySQLParser.SPOLY_CONTAINS_POINT_COM - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_POINT_COM_NEG - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE_NEG - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE_COM - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE_COM_NEG - 446)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON - 446)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON_NEG - 446)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM - 446)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM_NEG - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE_NEG - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE_COM - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE_COM_NEG - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE_NEG - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE_COM - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE_COM_NEG - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE_NEG - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE_COM - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE_COM_NEG - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE_NEG - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM - 446)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM_NEG - 446)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON - 446)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON_NEG - 446)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM - 446)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM_NEG - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE_NEG - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM - 446)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM_NEG - 446)) | (1 << (MySQLParser.STRANS_POLY - 446)) | (1 << (MySQLParser.STRANS_POLY_INVERSE - 446)) | (1 << (MySQLParser.SPOLY_ADD_POINT_AGGR - 446)) | (1 << (MySQLParser.SPOLY_AGGR - 446)) | (1 << (MySQLParser.SPATH - 446)) | (1 << (MySQLParser.SPATH_EQUAL - 446)) | (1 << (MySQLParser.SPATH_EQUAL_NEG - 446)) | (1 << (MySQLParser.SPATH_OVERLAP_PATH - 446)) | (1 << (MySQLParser.SPATH_OVERLAP_PATH_NEG - 446)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT - 446)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT_NEG - 446)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT_COM - 446)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT_COM_NEG - 446)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH - 446)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH_NEG - 446)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH_COM - 446)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH_COM_NEG - 446)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH - 446)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH_NEG - 446)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH_COM - 446)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH_COM_NEG - 446)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE - 446)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE_NEG - 446)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE_COM - 446)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE_COM_NEG - 446)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH - 446)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH_NEG - 446)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH_COM - 446)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH_COM_NEG - 446)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_PATH - 446)))) != 0) or ((((_la - 510)) & ~0x3f) == 0 and ((1 << (_la - 510)) & ((1 << (MySQLParser.SELLIPSE_OVERLAP_PATH_NEG - 510)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_PATH_COM - 510)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_PATH_COM_NEG - 510)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH - 510)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH_NEG - 510)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH_COM - 510)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH_COM_NEG - 510)) | (1 << (MySQLParser.SPOLY_OVERLAP_PATH - 510)) | (1 << (MySQLParser.SPOLY_OVERLAP_PATH_NEG - 510)) | (1 << (MySQLParser.SPOLY_OVERLAP_PATH_COM - 510)) | (1 << (MySQLParser.SPOLY_OVERLAP_PATH_COM_NEG - 510)) | (1 << (MySQLParser.STRANS_PATH - 510)) | (1 << (MySQLParser.STRANS_PATH_INVERSE - 510)) | (1 << (MySQLParser.SPATH_ADD_POINT_AGGR - 510)) | (1 << (MySQLParser.SPATH_AGGR - 510)) | (1 << (MySQLParser.SBOX - 510)) | (1 << (MySQLParser.SBOX_SW - 510)) | (1 << (MySQLParser.SBOX_SE - 510)) | (1 << (MySQLParser.SBOX_NW - 510)) | (1 << (MySQLParser.SBOX_NE - 510)) | (1 << (MySQLParser.SBOX_EQUAL - 510)) | (1 << (MySQLParser.SBOX_EQUAL_NEG - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX_NEG - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX_COM - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX_COM_NEG - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_BOX - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_BOX_NEG - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT_NEG - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT_COM - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT_COM_NEG - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE_NEG - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE_COM - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE_COM_NEG - 510)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX - 510)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX_NEG - 510)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX_COM - 510)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX_COM_NEG - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE_NEG - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE_COM - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE_COM_NEG - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE_NEG - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE_COM - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE_COM_NEG - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE_NEG - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE_COM - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE_COM_NEG - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE_NEG - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE_COM - 510)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE_COM_NEG - 510)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX - 510)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX_NEG - 510)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX_COM - 510)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX_COM_NEG - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE_NEG - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE_COM - 510)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE_COM_NEG - 510)))) != 0) or ((((_la - 574)) & ~0x3f) == 0 and ((1 << (_la - 574)) & ((1 << (MySQLParser.SBOX_CONTAINS_POLY - 574)) | (1 << (MySQLParser.SBOX_CONTAINS_POLY_NEG - 574)) | (1 << (MySQLParser.SBOX_CONTAINS_POLY_COM - 574)) | (1 << (MySQLParser.SBOX_CONTAINS_POLY_COM_NEG - 574)) | (1 << (MySQLParser.SPOLY_CONTAINS_BOX - 574)) | (1 << (MySQLParser.SPOLY_CONTAINS_BOX_NEG - 574)) | (1 << (MySQLParser.SPOLY_CONTAINS_BOX_COM - 574)) | (1 << (MySQLParser.SPOLY_CONTAINS_BOX_COM_NEG - 574)) | (1 << (MySQLParser.SBOX_OVERLAP_POLY - 574)) | (1 << (MySQLParser.SBOX_OVERLAP_POLY_NEG - 574)) | (1 << (MySQLParser.SBOX_OVERLAP_POLY_COM - 574)) | (1 << (MySQLParser.SBOX_OVERLAP_POLY_COM_NEG - 574)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH - 574)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH_NEG - 574)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH_COM - 574)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH_COM_NEG - 574)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH - 574)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH_NEG - 574)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH_COM - 574)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH_COM_NEG - 574)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Mysql_udf_functionsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Mysql_udf_functionsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def STRRPOS(self):
            return self.getToken(MySQLParser.STRRPOS, 0)

        def IDLE(self):
            return self.getToken(MySQLParser.IDLE, 0)

        def ANGDIST(self):
            return self.getToken(MySQLParser.ANGDIST, 0)

        def HILBERTKEY(self):
            return self.getToken(MySQLParser.HILBERTKEY, 0)

        def COORDFROMHILBERTKEY(self):
            return self.getToken(MySQLParser.COORDFROMHILBERTKEY, 0)

        def SUM_OF_SQUARES(self):
            return self.getToken(MySQLParser.SUM_OF_SQUARES, 0)

        def PARTITADD_SUM_OF_SQARES(self):
            return self.getToken(MySQLParser.PARTITADD_SUM_OF_SQARES, 0)

        def GAIA_HEALPIX(self):
            return self.getToken(MySQLParser.GAIA_HEALPIX, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_mysql_udf_functions

        def enterRule(self, listener):
            if hasattr(listener, "enterMysql_udf_functions"):
                listener.enterMysql_udf_functions(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMysql_udf_functions"):
                listener.exitMysql_udf_functions(self)




    def mysql_udf_functions(self):

        localctx = MySQLParser.Mysql_udf_functionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_mysql_udf_functions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 243
            _la = self._input.LA(1)
            if not(((((_la - 594)) & ~0x3f) == 0 and ((1 << (_la - 594)) & ((1 << (MySQLParser.STRRPOS - 594)) | (1 << (MySQLParser.IDLE - 594)) | (1 << (MySQLParser.ANGDIST - 594)) | (1 << (MySQLParser.HILBERTKEY - 594)) | (1 << (MySQLParser.COORDFROMHILBERTKEY - 594)) | (1 << (MySQLParser.SUM_OF_SQUARES - 594)) | (1 << (MySQLParser.PARTITADD_SUM_OF_SQARES - 594)) | (1 << (MySQLParser.GAIA_HEALPIX - 594)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FunctionListContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.FunctionListContext, self).__init__(parent, invokingState)
            self.parser = parser

        def number_functions(self):
            return self.getTypedRuleContext(MySQLParser.Number_functionsContext,0)


        def char_functions(self):
            return self.getTypedRuleContext(MySQLParser.Char_functionsContext,0)


        def time_functions(self):
            return self.getTypedRuleContext(MySQLParser.Time_functionsContext,0)


        def other_functions(self):
            return self.getTypedRuleContext(MySQLParser.Other_functionsContext,0)


        def mysql_sphere_functions(self):
            return self.getTypedRuleContext(MySQLParser.Mysql_sphere_functionsContext,0)


        def mysql_udf_functions(self):
            return self.getTypedRuleContext(MySQLParser.Mysql_udf_functionsContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_functionList

        def enterRule(self, listener):
            if hasattr(listener, "enterFunctionList"):
                listener.enterFunctionList(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFunctionList"):
                listener.exitFunctionList(self)




    def functionList(self):

        localctx = MySQLParser.FunctionListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_functionList)
        try:
            self.state = 251
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,10,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 245
                self.number_functions()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 246
                self.char_functions()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 247
                self.time_functions()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 248
                self.other_functions()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 249
                self.mysql_sphere_functions()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 250
                self.mysql_udf_functions()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Literal_valueContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Literal_valueContext, self).__init__(parent, invokingState)
            self.parser = parser

        def string_literal(self):
            return self.getTypedRuleContext(MySQLParser.String_literalContext,0)


        def number_literal(self):
            return self.getTypedRuleContext(MySQLParser.Number_literalContext,0)


        def hex_literal(self):
            return self.getTypedRuleContext(MySQLParser.Hex_literalContext,0)


        def boolean_literal(self):
            return self.getTypedRuleContext(MySQLParser.Boolean_literalContext,0)


        def bit_literal(self):
            return self.getTypedRuleContext(MySQLParser.Bit_literalContext,0)


        def NULL_SYM(self):
            return self.getToken(MySQLParser.NULL_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_literal_value

        def enterRule(self, listener):
            if hasattr(listener, "enterLiteral_value"):
                listener.enterLiteral_value(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitLiteral_value"):
                listener.exitLiteral_value(self)




    def literal_value(self):

        localctx = MySQLParser.Literal_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_literal_value)
        try:
            self.state = 259
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [MySQLParser.TEXT_STRING]:
                self.enterOuterAlt(localctx, 1)
                self.state = 253
                self.string_literal()
                pass
            elif token in [MySQLParser.PLUS, MySQLParser.MINUS, MySQLParser.INTEGER_NUM, MySQLParser.REAL_NUMBER]:
                self.enterOuterAlt(localctx, 2)
                self.state = 254
                self.number_literal()
                pass
            elif token in [MySQLParser.HEX_DIGIT]:
                self.enterOuterAlt(localctx, 3)
                self.state = 255
                self.hex_literal()
                pass
            elif token in [MySQLParser.FALSE_SYM, MySQLParser.TRUE_SYM]:
                self.enterOuterAlt(localctx, 4)
                self.state = 256
                self.boolean_literal()
                pass
            elif token in [MySQLParser.BIT_NUM]:
                self.enterOuterAlt(localctx, 5)
                self.state = 257
                self.bit_literal()
                pass
            elif token in [MySQLParser.NULL_SYM]:
                self.enterOuterAlt(localctx, 6)
                self.state = 258
                self.match(MySQLParser.NULL_SYM)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Select_expressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Select_expressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def SELECT(self):
            return self.getToken(MySQLParser.SELECT, 0)

        def select_list(self):
            return self.getTypedRuleContext(MySQLParser.Select_listContext,0)


        def HIGH_PRIORITY(self):
            return self.getToken(MySQLParser.HIGH_PRIORITY, 0)

        def STRAIGHT_JOIN(self):
            return self.getToken(MySQLParser.STRAIGHT_JOIN, 0)

        def SQL_SMALL_RESULT(self):
            return self.getToken(MySQLParser.SQL_SMALL_RESULT, 0)

        def SQL_BIG_RESULT(self):
            return self.getToken(MySQLParser.SQL_BIG_RESULT, 0)

        def SQL_BUFFER_RESULT(self):
            return self.getToken(MySQLParser.SQL_BUFFER_RESULT, 0)

        def SQL_CALC_FOUND_ROWS(self):
            return self.getToken(MySQLParser.SQL_CALC_FOUND_ROWS, 0)

        def FROM(self):
            return self.getToken(MySQLParser.FROM, 0)

        def table_references(self):
            return self.getTypedRuleContext(MySQLParser.Table_referencesContext,0)


        def orderby_clause(self):
            return self.getTypedRuleContext(MySQLParser.Orderby_clauseContext,0)


        def limit_clause(self):
            return self.getTypedRuleContext(MySQLParser.Limit_clauseContext,0)


        def SEMI(self):
            return self.getToken(MySQLParser.SEMI, 0)

        def ALL(self):
            return self.getToken(MySQLParser.ALL, 0)

        def DISTINCT(self):
            return self.getToken(MySQLParser.DISTINCT, 0)

        def DISTINCTROW(self):
            return self.getToken(MySQLParser.DISTINCTROW, 0)

        def SQL_CACHE_SYM(self):
            return self.getToken(MySQLParser.SQL_CACHE_SYM, 0)

        def SQL_NO_CACHE_SYM(self):
            return self.getToken(MySQLParser.SQL_NO_CACHE_SYM, 0)

        def FOR_SYM(self):
            return self.getToken(MySQLParser.FOR_SYM, 0)

        def UPDATE(self):
            return self.getToken(MySQLParser.UPDATE, 0)

        def LOCK(self):
            return self.getToken(MySQLParser.LOCK, 0)

        def IN_SYM(self):
            return self.getToken(MySQLParser.IN_SYM, 0)

        def SHARE_SYM(self):
            return self.getToken(MySQLParser.SHARE_SYM, 0)

        def MODE_SYM(self):
            return self.getToken(MySQLParser.MODE_SYM, 0)

        def partition_clause(self):
            return self.getTypedRuleContext(MySQLParser.Partition_clauseContext,0)


        def where_clause(self):
            return self.getTypedRuleContext(MySQLParser.Where_clauseContext,0)


        def groupby_clause(self):
            return self.getTypedRuleContext(MySQLParser.Groupby_clauseContext,0)


        def having_clause(self):
            return self.getTypedRuleContext(MySQLParser.Having_clauseContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_select_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterSelect_expression"):
                listener.enterSelect_expression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSelect_expression"):
                listener.exitSelect_expression(self)




    def select_expression(self):

        localctx = MySQLParser.Select_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_select_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 261
            self.match(MySQLParser.SELECT)
            self.state = 263
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.ALL or _la==MySQLParser.DISTINCT or _la==MySQLParser.DISTINCTROW:
                self.state = 262
                _la = self._input.LA(1)
                if not(_la==MySQLParser.ALL or _la==MySQLParser.DISTINCT or _la==MySQLParser.DISTINCTROW):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


            self.state = 266
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.HIGH_PRIORITY:
                self.state = 265
                self.match(MySQLParser.HIGH_PRIORITY)


            self.state = 269
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.STRAIGHT_JOIN:
                self.state = 268
                self.match(MySQLParser.STRAIGHT_JOIN)


            self.state = 272
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.SQL_SMALL_RESULT:
                self.state = 271
                self.match(MySQLParser.SQL_SMALL_RESULT)


            self.state = 275
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.SQL_BIG_RESULT:
                self.state = 274
                self.match(MySQLParser.SQL_BIG_RESULT)


            self.state = 278
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.SQL_BUFFER_RESULT:
                self.state = 277
                self.match(MySQLParser.SQL_BUFFER_RESULT)


            self.state = 281
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.SQL_CACHE_SYM or _la==MySQLParser.SQL_NO_CACHE_SYM:
                self.state = 280
                _la = self._input.LA(1)
                if not(_la==MySQLParser.SQL_CACHE_SYM or _la==MySQLParser.SQL_NO_CACHE_SYM):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


            self.state = 284
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.SQL_CALC_FOUND_ROWS:
                self.state = 283
                self.match(MySQLParser.SQL_CALC_FOUND_ROWS)


            self.state = 286
            self.select_list()
            self.state = 301
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.FROM:
                self.state = 287
                self.match(MySQLParser.FROM)
                self.state = 288
                self.table_references()
                self.state = 290
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.PARTITION_SYM:
                    self.state = 289
                    self.partition_clause()


                self.state = 293
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.WHERE:
                    self.state = 292
                    self.where_clause()


                self.state = 296
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.GROUP_SYM:
                    self.state = 295
                    self.groupby_clause()


                self.state = 299
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.HAVING:
                    self.state = 298
                    self.having_clause()




            self.state = 304
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.ORDER_SYM:
                self.state = 303
                self.orderby_clause()


            self.state = 307
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.LIMIT or _la==MySQLParser.INTEGER_NUM:
                self.state = 306
                self.limit_clause()


            self.state = 315
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [MySQLParser.FOR_SYM]:
                self.state = 309
                self.match(MySQLParser.FOR_SYM)
                self.state = 310
                self.match(MySQLParser.UPDATE)
                pass
            elif token in [MySQLParser.LOCK]:
                self.state = 311
                self.match(MySQLParser.LOCK)
                self.state = 312
                self.match(MySQLParser.IN_SYM)
                self.state = 313
                self.match(MySQLParser.SHARE_SYM)
                self.state = 314
                self.match(MySQLParser.MODE_SYM)
                pass
            elif token in [MySQLParser.UNION_SYM, MySQLParser.SEMI, MySQLParser.RPAREN]:
                pass
            else:
                pass
            self.state = 318
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,28,self._ctx)
            if la_ == 1:
                self.state = 317
                self.match(MySQLParser.SEMI)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AliasContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.AliasContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(MySQLParser.ID, 0)

        def AS_SYM(self):
            return self.getToken(MySQLParser.AS_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_alias

        def enterRule(self, listener):
            if hasattr(listener, "enterAlias"):
                listener.enterAlias(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitAlias"):
                listener.exitAlias(self)




    def alias(self):

        localctx = MySQLParser.AliasContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_alias)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 321
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.AS_SYM:
                self.state = 320
                self.match(MySQLParser.AS_SYM)


            self.state = 323
            self.match(MySQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Bit_exprContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Bit_exprContext, self).__init__(parent, invokingState)
            self.parser = parser

        def factor1(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Factor1Context)
            else:
                return self.getTypedRuleContext(MySQLParser.Factor1Context,i)


        def VERTBAR(self):
            return self.getToken(MySQLParser.VERTBAR, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_bit_expr

        def enterRule(self, listener):
            if hasattr(listener, "enterBit_expr"):
                listener.enterBit_expr(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBit_expr"):
                listener.exitBit_expr(self)




    def bit_expr(self):

        localctx = MySQLParser.Bit_exprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_bit_expr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 325
            self.factor1()
            self.state = 328
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,30,self._ctx)
            if la_ == 1:
                self.state = 326
                self.match(MySQLParser.VERTBAR)
                self.state = 327
                self.factor1()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Bool_primaryContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Bool_primaryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def predicate(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.PredicateContext)
            else:
                return self.getTypedRuleContext(MySQLParser.PredicateContext,i)


        def relational_op(self):
            return self.getTypedRuleContext(MySQLParser.Relational_opContext,0)


        def EXISTS(self):
            return self.getToken(MySQLParser.EXISTS, 0)

        def subquery(self):
            return self.getTypedRuleContext(MySQLParser.SubqueryContext,0)


        def NOT_SYM(self):
            return self.getToken(MySQLParser.NOT_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_bool_primary

        def enterRule(self, listener):
            if hasattr(listener, "enterBool_primary"):
                listener.enterBool_primary(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBool_primary"):
                listener.exitBool_primary(self)




    def bool_primary(self):

        localctx = MySQLParser.Bool_primaryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_bool_primary)
        self._la = 0 # Token type
        try:
            self.state = 341
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,33,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 330
                self.predicate()
                self.state = 334
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,31,self._ctx)
                if la_ == 1:
                    self.state = 331
                    self.relational_op()
                    self.state = 332
                    self.predicate()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 337
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.NOT_SYM:
                    self.state = 336
                    self.match(MySQLParser.NOT_SYM)


                self.state = 339
                self.match(MySQLParser.EXISTS)
                self.state = 340
                self.subquery()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Case_when_statementContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Case_when_statementContext, self).__init__(parent, invokingState)
            self.parser = parser

        def CASE_SYM(self):
            return self.getToken(MySQLParser.CASE_SYM, 0)

        def END_SYM(self):
            return self.getToken(MySQLParser.END_SYM, 0)

        def case_when_statement1(self):
            return self.getTypedRuleContext(MySQLParser.Case_when_statement1Context,0)


        def case_when_statement2(self):
            return self.getTypedRuleContext(MySQLParser.Case_when_statement2Context,0)


        def ELSE_SYM(self):
            return self.getToken(MySQLParser.ELSE_SYM, 0)

        def bit_expr(self):
            return self.getTypedRuleContext(MySQLParser.Bit_exprContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_case_when_statement

        def enterRule(self, listener):
            if hasattr(listener, "enterCase_when_statement"):
                listener.enterCase_when_statement(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCase_when_statement"):
                listener.exitCase_when_statement(self)




    def case_when_statement(self):

        localctx = MySQLParser.Case_when_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_case_when_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 343
            self.match(MySQLParser.CASE_SYM)
            self.state = 346
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [MySQLParser.WHEN_SYM]:
                self.state = 344
                self.case_when_statement1()
                pass
            elif token in [MySQLParser.ABS, MySQLParser.ACOS, MySQLParser.ADDDATE, MySQLParser.ADDTIME, MySQLParser.AES_DECRYPT, MySQLParser.AES_ENCRYPT, MySQLParser.ASCII_SYM, MySQLParser.ASIN, MySQLParser.ATAN, MySQLParser.ATAN2, MySQLParser.AVG, MySQLParser.BENCHMARK, MySQLParser.BIN, MySQLParser.BINARY, MySQLParser.BIT_AND, MySQLParser.BIT_COUNT, MySQLParser.BIT_LENGTH, MySQLParser.BIT_OR, MySQLParser.BIT_XOR, MySQLParser.CASE_SYM, MySQLParser.CAST_SYM, MySQLParser.CEIL, MySQLParser.CEILING, MySQLParser.CHAR, MySQLParser.CHARSET, MySQLParser.CHAR_LENGTH, MySQLParser.COERCIBILITY, MySQLParser.COLLATION, MySQLParser.CONCAT, MySQLParser.CONCAT_WS, MySQLParser.CONNECTION_ID, MySQLParser.CONV, MySQLParser.CONVERT_SYM, MySQLParser.CONVERT_TZ, MySQLParser.COS, MySQLParser.COT, MySQLParser.COUNT, MySQLParser.CRC32, MySQLParser.CURDATE, MySQLParser.CURRENT_USER, MySQLParser.CURTIME, MySQLParser.DATABASE, MySQLParser.DATEDIFF, MySQLParser.DATE_ADD, MySQLParser.DATE_FORMAT, MySQLParser.DATE_SUB, MySQLParser.DATE_SYM, MySQLParser.DAYNAME, MySQLParser.DAYOFMONTH, MySQLParser.DAYOFWEEK, MySQLParser.DAYOFYEAR, MySQLParser.DECODE, MySQLParser.DEFAULT, MySQLParser.DEGREES, MySQLParser.DES_DECRYPT, MySQLParser.DES_ENCRYPT, MySQLParser.ELT, MySQLParser.ENCODE, MySQLParser.ENCRYPT, MySQLParser.EXISTS, MySQLParser.EXP, MySQLParser.EXPORT_SET, MySQLParser.EXTRACT, MySQLParser.FALSE_SYM, MySQLParser.FIELD, MySQLParser.FIND_IN_SET, MySQLParser.FLOOR, MySQLParser.FORMAT, MySQLParser.FOUND_ROWS, MySQLParser.FROM_BASE64, MySQLParser.FROM_DAYS, MySQLParser.FROM_UNIXTIME, MySQLParser.GET_FORMAT, MySQLParser.GET_LOCK, MySQLParser.GROUP_CONCAT, MySQLParser.HEX, MySQLParser.HOUR, MySQLParser.IF, MySQLParser.IFNULL, MySQLParser.INET_ATON, MySQLParser.INET_NTOA, MySQLParser.INSERT, MySQLParser.INSTR, MySQLParser.INTERVAL_SYM, MySQLParser.IS_FREE_LOCK, MySQLParser.IS_USED_LOCK, MySQLParser.LAST_DAY, MySQLParser.LAST_INSERT_ID, MySQLParser.LEFT, MySQLParser.LENGTH, MySQLParser.LN, MySQLParser.LOAD_FILE, MySQLParser.LOCATE, MySQLParser.LOG, MySQLParser.LOG10, MySQLParser.LOG2, MySQLParser.LOWER, MySQLParser.LPAD, MySQLParser.LTRIM, MySQLParser.MAKEDATE, MySQLParser.MAKETIME, MySQLParser.MAKE_SET, MySQLParser.MASTER_POS_WAIT, MySQLParser.MATCH, MySQLParser.MAX_SYM, MySQLParser.MD5, MySQLParser.MICROSECOND, MySQLParser.MID, MySQLParser.MINUTE, MySQLParser.MIN_SYM, MySQLParser.MOD, MySQLParser.MONTH, MySQLParser.MONTHNAME, MySQLParser.NAME_CONST, MySQLParser.NOW, MySQLParser.NULL_SYM, MySQLParser.OCT, MySQLParser.OLD_PASSWORD, MySQLParser.ORD, MySQLParser.PASSWORD, MySQLParser.PERIOD_ADD, MySQLParser.PERIOD_DIFF, MySQLParser.PI, MySQLParser.POW, MySQLParser.POWER, MySQLParser.QUARTER, MySQLParser.QUOTE, MySQLParser.RADIANS, MySQLParser.RAND, MySQLParser.RELEASE_LOCK, MySQLParser.REPEAT, MySQLParser.REPLACE, MySQLParser.REVERSE, MySQLParser.RIGHT, MySQLParser.ROUND, MySQLParser.ROW_SYM, MySQLParser.RPAD, MySQLParser.RTRIM, MySQLParser.SCHEMA, MySQLParser.SECOND, MySQLParser.SEC_TO_TIME, MySQLParser.SESSION_USER, MySQLParser.SIGN, MySQLParser.SIN, MySQLParser.SLEEP, MySQLParser.SOUNDEX, MySQLParser.SPACE, MySQLParser.SQRT, MySQLParser.STD, MySQLParser.STDDEV, MySQLParser.STDDEV_POP, MySQLParser.STDDEV_SAMP, MySQLParser.STRCMP, MySQLParser.STR_TO_DATE, MySQLParser.SUBSTRING, MySQLParser.SUBSTRING_INDEX, MySQLParser.SUBTIME, MySQLParser.SUM, MySQLParser.SYSDATE, MySQLParser.SYSTEM_USER, MySQLParser.TAN, MySQLParser.TIMEDIFF, MySQLParser.TIMESTAMP, MySQLParser.TIMESTAMPADD, MySQLParser.TIMESTAMPDIFF, MySQLParser.TIME_FORMAT, MySQLParser.TIME_SYM, MySQLParser.TIME_TO_SEC, MySQLParser.TO_BASE64, MySQLParser.TO_DAYS, MySQLParser.TO_SECONDS, MySQLParser.TRIM, MySQLParser.TRUE_SYM, MySQLParser.TRUNCATE, MySQLParser.UNHEX, MySQLParser.UNIX_TIMESTAMP, MySQLParser.UPPER, MySQLParser.USER, MySQLParser.UTC_DATE, MySQLParser.UTC_TIME, MySQLParser.UTC_TIMESTAMP, MySQLParser.UUID, MySQLParser.VALUES, MySQLParser.VARIANCE, MySQLParser.VAR_POP, MySQLParser.VAR_SAMP, MySQLParser.VERSION_SYM, MySQLParser.WEEK, MySQLParser.WEEKDAY, MySQLParser.WEEKOFYEAR, MySQLParser.WEIGHT_STRING, MySQLParser.YEAR, MySQLParser.YEARWEEK, MySQLParser.SDIST, MySQLParser.SAREA, MySQLParser.SCENTER, MySQLParser.SCIRCUM, MySQLParser.SLENGTH, MySQLParser.SSWAP, MySQLParser.SNPOINTS, MySQLParser.SSTR, MySQLParser.MYSQL_SPHERE_VERSION, MySQLParser.SRCONTAINSL, MySQLParser.SLCONTAINSR, MySQLParser.SRNOTCONTAINSL, MySQLParser.SLNOTCONTAINSR, MySQLParser.SOVERLAPS, MySQLParser.SNOTOVERLAPS, MySQLParser.SEQUAL, MySQLParser.SNOTEQUAL, MySQLParser.STRANSFORM, MySQLParser.SINVERSE, MySQLParser.SPOINT, MySQLParser.SPOINT_LONG, MySQLParser.SPOINT_LAT, MySQLParser.SPOINT_X, MySQLParser.SPOINT_Y, MySQLParser.SPOINT_Z, MySQLParser.SPOINT_EQUAL, MySQLParser.STRANS, MySQLParser.STRANS_POINT, MySQLParser.STRANS_POINT_INVERSE, MySQLParser.STRANS_EQUAL, MySQLParser.STRANS_EQUAL_NEG, MySQLParser.STRANS_PHI, MySQLParser.STRANS_THETA, MySQLParser.STRANS_PSI, MySQLParser.STRANS_AXES, MySQLParser.STRANS_INVERT, MySQLParser.STRANS_ZXZ, MySQLParser.STRANS_TRANS, MySQLParser.STRANS_TRANS_INV, MySQLParser.SCIRCLE, MySQLParser.SCIRCLE_RADIUS, MySQLParser.SCIRCLE_EQUAL, MySQLParser.SCIRCLE_EQUAL_NEG, MySQLParser.SCIRCLE_OVERLAP, MySQLParser.SCIRCLE_OVERLAP_NEG, MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE, MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE_NEG, MySQLParser.SCIRCLE_CONTAINS_CIRCLE, MySQLParser.SCIRCLE_CONTAINS_CIRCLE_NEG, MySQLParser.SPOINT_CONTAINED_BY_CIRCLE, MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_NEG, MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM, MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM_NEG, MySQLParser.STRANS_CIRCLE, MySQLParser.STRANS_CIRCLE_INVERSE, MySQLParser.SLINE, MySQLParser.SMERIDIAN, MySQLParser.SLINE_BEG, MySQLParser.SLINE_END, MySQLParser.SLINE_EQUAL, MySQLParser.SLINE_EQUAL_NEG, MySQLParser.SLINE_TURN, MySQLParser.SLINE_CROSSES, MySQLParser.SLINE_CROSSES_NEG, MySQLParser.SLINE_OVERLAP, MySQLParser.SLINE_CONTAINS_POINT, MySQLParser.SLINE_CONTAINS_POINT_COM, MySQLParser.SLINE_CONTAINS_POINT_NEG, MySQLParser.SLINE_CONTAINS_POINT_COM_NEG, MySQLParser.STRANS_LINE, MySQLParser.STRANS_LINE_INVERSE, MySQLParser.SLINE_OVERLAP_CIRCLE, MySQLParser.SLINE_OVERLAP_CIRCLE_COM, MySQLParser.SLINE_OVERLAP_CIRCLE_NEG, MySQLParser.SLINE_OVERLAP_CIRCLE_COM_NEG, MySQLParser.SCIRCLE_CONTAINS_LINE, MySQLParser.SCIRCLE_CONTAINS_LINE_COM, MySQLParser.SCIRCLE_CONTAINS_LINE_NEG, MySQLParser.SCIRCLE_CONTAINS_LINE_COM_NEG, MySQLParser.SELLIPSE, MySQLParser.SELLIPSE_INC, MySQLParser.SELLIPSE_LRAD, MySQLParser.SELLIPSE_SRAD, MySQLParser.SELLIPSE_EQUAL, MySQLParser.SELLIPSE_EQUAL_NEG, MySQLParser.SELLIPSE_CONTAINS_ELLIPSE, MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_NEG, MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM, MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM_NEG, MySQLParser.SELLIPSE_OVERLAP_ELLIPSE, MySQLParser.SELLIPSE_OVERLAP_ELLIPSE_NEG, MySQLParser.SELLIPSE_CONTAINS_POINT, MySQLParser.SELLIPSE_CONTAINS_POINT_NEG, MySQLParser.SELLIPSE_CONTAINS_POINT_COM, MySQLParser.SELLIPSE_CONTAINS_POINT_COM_NEG, MySQLParser.SELLIPSE_CONTAINS_CIRCLE, MySQLParser.SELLIPSE_CONTAINS_CIRCLE_NEG, MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM, MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM_NEG, MySQLParser.SCIRCLE_CONTAINS_ELLIPSE, MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_NEG, MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM, MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM_NEG, MySQLParser.SELLIPSE_OVERLAP_CIRCLE, MySQLParser.SELLIPSE_OVERLAP_CIRCLE_NEG, MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM, MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM_NEG, MySQLParser.SELLIPSE_OVERLAP_LINE, MySQLParser.SELLIPSE_OVERLAP_LINE_NEG, MySQLParser.SELLIPSE_OVERLAP_LINE_COM, MySQLParser.SELLIPSE_OVERLAP_LINE_COM_NEG, MySQLParser.SELLIPSE_CONTAINS_LINE, MySQLParser.SELLIPSE_CONTAINS_LINE_NEG, MySQLParser.SELLIPSE_CONTAINS_LINE_COM, MySQLParser.SELLIPSE_CONTAINS_LINE_COM_NEG, MySQLParser.STRANS_ELLIPSE, MySQLParser.STRANS_ELLIPSE_INVERSE, MySQLParser.SPOLY, MySQLParser.SPOLY_EQUAL, MySQLParser.SPOLY_EQUAL_NEG, MySQLParser.SPOLY_CONTAINS_POLYGON, MySQLParser.SPOLY_CONTAINS_POLYGON_NEG, MySQLParser.SPOLY_CONTAINS_POLYGON_COM, MySQLParser.SPOLY_CONTAINS_POLYGON_COM_NEG, MySQLParser.SPOLY_OVERLAP_POLYGON, MySQLParser.SPOLY_OVERLAP_POLYGON_NEG, MySQLParser.SPOLY_CONTAINS_POINT, MySQLParser.SPOLY_CONTAINS_POINT_NEG, MySQLParser.SPOLY_CONTAINS_POINT_COM, MySQLParser.SPOLY_CONTAINS_POINT_COM_NEG, MySQLParser.SPOLY_CONTAINS_CIRCLE, MySQLParser.SPOLY_CONTAINS_CIRCLE_NEG, MySQLParser.SPOLY_CONTAINS_CIRCLE_COM, MySQLParser.SPOLY_CONTAINS_CIRCLE_COM_NEG, MySQLParser.SCIRCLE_CONTAINS_POLYGON, MySQLParser.SCIRCLE_CONTAINS_POLYGON_NEG, MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM, MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM_NEG, MySQLParser.SPOLY_OVERLAP_CIRCLE, MySQLParser.SPOLY_OVERLAP_CIRCLE_NEG, MySQLParser.SPOLY_OVERLAP_CIRCLE_COM, MySQLParser.SPOLY_OVERLAP_CIRCLE_COM_NEG, MySQLParser.SPOLY_CONTAINS_LINE, MySQLParser.SPOLY_CONTAINS_LINE_NEG, MySQLParser.SPOLY_CONTAINS_LINE_COM, MySQLParser.SPOLY_CONTAINS_LINE_COM_NEG, MySQLParser.SPOLY_OVERLAP_LINE, MySQLParser.SPOLY_OVERLAP_LINE_NEG, MySQLParser.SPOLY_OVERLAP_LINE_COM, MySQLParser.SPOLY_OVERLAP_LINE_COM_NEG, MySQLParser.SPOLY_CONTAINS_ELLIPSE, MySQLParser.SPOLY_CONTAINS_ELLIPSE_NEG, MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM, MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM_NEG, MySQLParser.SELLIPSE_CONTAINS_POLYGON, MySQLParser.SELLIPSE_CONTAINS_POLYGON_NEG, MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM, MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM_NEG, MySQLParser.SPOLY_OVERLAP_ELLIPSE, MySQLParser.SPOLY_OVERLAP_ELLIPSE_NEG, MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM, MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM_NEG, MySQLParser.STRANS_POLY, MySQLParser.STRANS_POLY_INVERSE, MySQLParser.SPOLY_ADD_POINT_AGGR, MySQLParser.SPOLY_AGGR, MySQLParser.SPATH, MySQLParser.SPATH_EQUAL, MySQLParser.SPATH_EQUAL_NEG, MySQLParser.SPATH_OVERLAP_PATH, MySQLParser.SPATH_OVERLAP_PATH_NEG, MySQLParser.SPATH_CONTAINS_POINT, MySQLParser.SPATH_CONTAINS_POINT_NEG, MySQLParser.SPATH_CONTAINS_POINT_COM, MySQLParser.SPATH_CONTAINS_POINT_COM_NEG, MySQLParser.SCIRCLE_CONTAINS_PATH, MySQLParser.SCIRCLE_CONTAINS_PATH_NEG, MySQLParser.SCIRCLE_CONTAINS_PATH_COM, MySQLParser.SCIRCLE_CONTAINS_PATH_COM_NEG, MySQLParser.SCIRCLE_OVERLAP_PATH, MySQLParser.SCIRCLE_OVERLAP_PATH_NEG, MySQLParser.SCIRCLE_OVERLAP_PATH_COM, MySQLParser.SCIRCLE_OVERLAP_PATH_COM_NEG, MySQLParser.SPATH_OVERLAP_LINE, MySQLParser.SPATH_OVERLAP_LINE_NEG, MySQLParser.SPATH_OVERLAP_LINE_COM, MySQLParser.SPATH_OVERLAP_LINE_COM_NEG, MySQLParser.SELLIPSE_CONTAINS_PATH, MySQLParser.SELLIPSE_CONTAINS_PATH_NEG, MySQLParser.SELLIPSE_CONTAINS_PATH_COM, MySQLParser.SELLIPSE_CONTAINS_PATH_COM_NEG, MySQLParser.SELLIPSE_OVERLAP_PATH, MySQLParser.SELLIPSE_OVERLAP_PATH_NEG, MySQLParser.SELLIPSE_OVERLAP_PATH_COM, MySQLParser.SELLIPSE_OVERLAP_PATH_COM_NEG, MySQLParser.SPOLY_CONTAINS_PATH, MySQLParser.SPOLY_CONTAINS_PATH_NEG, MySQLParser.SPOLY_CONTAINS_PATH_COM, MySQLParser.SPOLY_CONTAINS_PATH_COM_NEG, MySQLParser.SPOLY_OVERLAP_PATH, MySQLParser.SPOLY_OVERLAP_PATH_NEG, MySQLParser.SPOLY_OVERLAP_PATH_COM, MySQLParser.SPOLY_OVERLAP_PATH_COM_NEG, MySQLParser.STRANS_PATH, MySQLParser.STRANS_PATH_INVERSE, MySQLParser.SPATH_ADD_POINT_AGGR, MySQLParser.SPATH_AGGR, MySQLParser.SBOX, MySQLParser.SBOX_SW, MySQLParser.SBOX_SE, MySQLParser.SBOX_NW, MySQLParser.SBOX_NE, MySQLParser.SBOX_EQUAL, MySQLParser.SBOX_EQUAL_NEG, MySQLParser.SBOX_CONTAINS_BOX, MySQLParser.SBOX_CONTAINS_BOX_NEG, MySQLParser.SBOX_CONTAINS_BOX_COM, MySQLParser.SBOX_CONTAINS_BOX_COM_NEG, MySQLParser.SBOX_OVERLAP_BOX, MySQLParser.SBOX_OVERLAP_BOX_NEG, MySQLParser.SBOX_CONTAINS_POINT, MySQLParser.SBOX_CONTAINS_POINT_NEG, MySQLParser.SBOX_CONTAINS_POINT_COM, MySQLParser.SBOX_CONTAINS_POINT_COM_NEG, MySQLParser.SBOX_CONTAINS_CIRCLE, MySQLParser.SBOX_CONTAINS_CIRCLE_NEG, MySQLParser.SBOX_CONTAINS_CIRCLE_COM, MySQLParser.SBOX_CONTAINS_CIRCLE_COM_NEG, MySQLParser.SCIRCLE_CONTAINS_BOX, MySQLParser.SCIRCLE_CONTAINS_BOX_NEG, MySQLParser.SCIRCLE_CONTAINS_BOX_COM, MySQLParser.SCIRCLE_CONTAINS_BOX_COM_NEG, MySQLParser.SBOX_OVERLAP_CIRCLE, MySQLParser.SBOX_OVERLAP_CIRCLE_NEG, MySQLParser.SBOX_OVERLAP_CIRCLE_COM, MySQLParser.SBOX_OVERLAP_CIRCLE_COM_NEG, MySQLParser.SBOX_CONTAINS_LINE, MySQLParser.SBOX_CONTAINS_LINE_NEG, MySQLParser.SBOX_CONTAINS_LINE_COM, MySQLParser.SBOX_CONTAINS_LINE_COM_NEG, MySQLParser.SBOX_OVERLAP_LINE, MySQLParser.SBOX_OVERLAP_LINE_NEG, MySQLParser.SBOX_OVERLAP_LINE_COM, MySQLParser.SBOX_OVERLAP_LINE_COM_NEG, MySQLParser.SBOX_CONTAINS_ELLIPSE, MySQLParser.SBOX_CONTAINS_ELLIPSE_NEG, MySQLParser.SBOX_CONTAINS_ELLIPSE_COM, MySQLParser.SBOX_CONTAINS_ELLIPSE_COM_NEG, MySQLParser.SELLIPSE_CONTAINS_BOX, MySQLParser.SELLIPSE_CONTAINS_BOX_NEG, MySQLParser.SELLIPSE_CONTAINS_BOX_COM, MySQLParser.SELLIPSE_CONTAINS_BOX_COM_NEG, MySQLParser.SBOX_OVERLAP_ELLIPSE, MySQLParser.SBOX_OVERLAP_ELLIPSE_NEG, MySQLParser.SBOX_OVERLAP_ELLIPSE_COM, MySQLParser.SBOX_OVERLAP_ELLIPSE_COM_NEG, MySQLParser.SBOX_CONTAINS_POLY, MySQLParser.SBOX_CONTAINS_POLY_NEG, MySQLParser.SBOX_CONTAINS_POLY_COM, MySQLParser.SBOX_CONTAINS_POLY_COM_NEG, MySQLParser.SPOLY_CONTAINS_BOX, MySQLParser.SPOLY_CONTAINS_BOX_NEG, MySQLParser.SPOLY_CONTAINS_BOX_COM, MySQLParser.SPOLY_CONTAINS_BOX_COM_NEG, MySQLParser.SBOX_OVERLAP_POLY, MySQLParser.SBOX_OVERLAP_POLY_NEG, MySQLParser.SBOX_OVERLAP_POLY_COM, MySQLParser.SBOX_OVERLAP_POLY_COM_NEG, MySQLParser.SBOX_CONTAINS_PATH, MySQLParser.SBOX_CONTAINS_PATH_NEG, MySQLParser.SBOX_CONTAINS_PATH_COM, MySQLParser.SBOX_CONTAINS_PATH_COM_NEG, MySQLParser.SBOX_OVERLAP_PATH, MySQLParser.SBOX_OVERLAP_PATH_NEG, MySQLParser.SBOX_OVERLAP_PATH_COM, MySQLParser.SBOX_OVERLAP_PATH_COM_NEG, MySQLParser.STRRPOS, MySQLParser.IDLE, MySQLParser.ANGDIST, MySQLParser.HILBERTKEY, MySQLParser.COORDFROMHILBERTKEY, MySQLParser.SUM_OF_SQUARES, MySQLParser.PARTITADD_SUM_OF_SQARES, MySQLParser.GAIA_HEALPIX, MySQLParser.LPAREN, MySQLParser.PLUS, MySQLParser.MINUS, MySQLParser.NEGATION, MySQLParser.INTEGER_NUM, MySQLParser.HEX_DIGIT, MySQLParser.BIT_NUM, MySQLParser.REAL_NUMBER, MySQLParser.TEXT_STRING, MySQLParser.ID, MySQLParser.USER_VAR]:
                self.state = 345
                self.case_when_statement2()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 350
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.ELSE_SYM:
                self.state = 348
                self.match(MySQLParser.ELSE_SYM)
                self.state = 349
                self.bit_expr()


            self.state = 352
            self.match(MySQLParser.END_SYM)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Case_when_statement1Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Case_when_statement1Context, self).__init__(parent, invokingState)
            self.parser = parser

        def WHEN_SYM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.WHEN_SYM)
            else:
                return self.getToken(MySQLParser.WHEN_SYM, i)

        def expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(MySQLParser.ExpressionContext,i)


        def THEN_SYM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.THEN_SYM)
            else:
                return self.getToken(MySQLParser.THEN_SYM, i)

        def bit_expr(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Bit_exprContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Bit_exprContext,i)


        def getRuleIndex(self):
            return MySQLParser.RULE_case_when_statement1

        def enterRule(self, listener):
            if hasattr(listener, "enterCase_when_statement1"):
                listener.enterCase_when_statement1(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCase_when_statement1"):
                listener.exitCase_when_statement1(self)




    def case_when_statement1(self):

        localctx = MySQLParser.Case_when_statement1Context(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_case_when_statement1)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 359 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 354
                self.match(MySQLParser.WHEN_SYM)
                self.state = 355
                self.expression()
                self.state = 356
                self.match(MySQLParser.THEN_SYM)
                self.state = 357
                self.bit_expr()
                self.state = 361 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==MySQLParser.WHEN_SYM):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Case_when_statement2Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Case_when_statement2Context, self).__init__(parent, invokingState)
            self.parser = parser

        def bit_expr(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Bit_exprContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Bit_exprContext,i)


        def WHEN_SYM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.WHEN_SYM)
            else:
                return self.getToken(MySQLParser.WHEN_SYM, i)

        def THEN_SYM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.THEN_SYM)
            else:
                return self.getToken(MySQLParser.THEN_SYM, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_case_when_statement2

        def enterRule(self, listener):
            if hasattr(listener, "enterCase_when_statement2"):
                listener.enterCase_when_statement2(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCase_when_statement2"):
                listener.exitCase_when_statement2(self)




    def case_when_statement2(self):

        localctx = MySQLParser.Case_when_statement2Context(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_case_when_statement2)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 363
            self.bit_expr()
            self.state = 369 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 364
                self.match(MySQLParser.WHEN_SYM)
                self.state = 365
                self.bit_expr()
                self.state = 366
                self.match(MySQLParser.THEN_SYM)
                self.state = 367
                self.bit_expr()
                self.state = 371 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==MySQLParser.WHEN_SYM):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Column_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Column_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(MySQLParser.LPAREN, 0)

        def column_spec(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Column_specContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Column_specContext,i)


        def RPAREN(self):
            return self.getToken(MySQLParser.RPAREN, 0)

        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.COMMA)
            else:
                return self.getToken(MySQLParser.COMMA, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_column_list

        def enterRule(self, listener):
            if hasattr(listener, "enterColumn_list"):
                listener.enterColumn_list(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitColumn_list"):
                listener.exitColumn_list(self)




    def column_list(self):

        localctx = MySQLParser.Column_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_column_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 373
            self.match(MySQLParser.LPAREN)
            self.state = 374
            self.column_spec()
            self.state = 379
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MySQLParser.COMMA:
                self.state = 375
                self.match(MySQLParser.COMMA)
                self.state = 376
                self.column_spec()
                self.state = 381
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 382
            self.match(MySQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Column_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Column_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(MySQLParser.ID, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_column_name

        def enterRule(self, listener):
            if hasattr(listener, "enterColumn_name"):
                listener.enterColumn_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitColumn_name"):
                listener.exitColumn_name(self)




    def column_name(self):

        localctx = MySQLParser.Column_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_column_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 384
            self.match(MySQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Column_specContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Column_specContext, self).__init__(parent, invokingState)
            self.parser = parser

        def column_name(self):
            return self.getTypedRuleContext(MySQLParser.Column_nameContext,0)


        def table_name(self):
            return self.getTypedRuleContext(MySQLParser.Table_nameContext,0)


        def DOT(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.DOT)
            else:
                return self.getToken(MySQLParser.DOT, i)

        def schema_name(self):
            return self.getTypedRuleContext(MySQLParser.Schema_nameContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_column_spec

        def enterRule(self, listener):
            if hasattr(listener, "enterColumn_spec"):
                listener.enterColumn_spec(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitColumn_spec"):
                listener.exitColumn_spec(self)




    def column_spec(self):

        localctx = MySQLParser.Column_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_column_spec)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 394
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,40,self._ctx)
            if la_ == 1:
                self.state = 389
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,39,self._ctx)
                if la_ == 1:
                    self.state = 386
                    self.schema_name()
                    self.state = 387
                    self.match(MySQLParser.DOT)


                self.state = 391
                self.table_name()
                self.state = 392
                self.match(MySQLParser.DOT)


            self.state = 396
            self.column_name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Displayed_columnContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Displayed_columnContext, self).__init__(parent, invokingState)
            self.parser = parser

        def table_spec(self):
            return self.getTypedRuleContext(MySQLParser.Table_specContext,0)


        def DOT(self):
            return self.getToken(MySQLParser.DOT, 0)

        def ASTERISK(self):
            return self.getToken(MySQLParser.ASTERISK, 0)

        def bit_expr(self):
            return self.getTypedRuleContext(MySQLParser.Bit_exprContext,0)


        def alias(self):
            return self.getTypedRuleContext(MySQLParser.AliasContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_displayed_column

        def enterRule(self, listener):
            if hasattr(listener, "enterDisplayed_column"):
                listener.enterDisplayed_column(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDisplayed_column"):
                listener.exitDisplayed_column(self)




    def displayed_column(self):

        localctx = MySQLParser.Displayed_columnContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_displayed_column)
        self._la = 0 # Token type
        try:
            self.state = 406
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,42,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 398
                self.table_spec()
                self.state = 399
                self.match(MySQLParser.DOT)
                self.state = 400
                self.match(MySQLParser.ASTERISK)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 402
                self.bit_expr()
                self.state = 404
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.AS_SYM or _la==MySQLParser.ID:
                    self.state = 403
                    self.alias()


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Exp_factor1Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Exp_factor1Context, self).__init__(parent, invokingState)
            self.parser = parser

        def exp_factor2(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Exp_factor2Context)
            else:
                return self.getTypedRuleContext(MySQLParser.Exp_factor2Context,i)


        def XOR(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.XOR)
            else:
                return self.getToken(MySQLParser.XOR, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_exp_factor1

        def enterRule(self, listener):
            if hasattr(listener, "enterExp_factor1"):
                listener.enterExp_factor1(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExp_factor1"):
                listener.exitExp_factor1(self)




    def exp_factor1(self):

        localctx = MySQLParser.Exp_factor1Context(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_exp_factor1)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 408
            self.exp_factor2()
            self.state = 413
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,43,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 409
                    self.match(MySQLParser.XOR)
                    self.state = 410
                    self.exp_factor2() 
                self.state = 415
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,43,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Exp_factor2Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Exp_factor2Context, self).__init__(parent, invokingState)
            self.parser = parser

        def exp_factor3(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Exp_factor3Context)
            else:
                return self.getTypedRuleContext(MySQLParser.Exp_factor3Context,i)


        def AND_SYM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.AND_SYM)
            else:
                return self.getToken(MySQLParser.AND_SYM, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_exp_factor2

        def enterRule(self, listener):
            if hasattr(listener, "enterExp_factor2"):
                listener.enterExp_factor2(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExp_factor2"):
                listener.exitExp_factor2(self)




    def exp_factor2(self):

        localctx = MySQLParser.Exp_factor2Context(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_exp_factor2)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 416
            self.exp_factor3()
            self.state = 421
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,44,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 417
                    self.match(MySQLParser.AND_SYM)
                    self.state = 418
                    self.exp_factor3() 
                self.state = 423
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,44,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Exp_factor3Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Exp_factor3Context, self).__init__(parent, invokingState)
            self.parser = parser

        def exp_factor4(self):
            return self.getTypedRuleContext(MySQLParser.Exp_factor4Context,0)


        def NOT_SYM(self):
            return self.getToken(MySQLParser.NOT_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_exp_factor3

        def enterRule(self, listener):
            if hasattr(listener, "enterExp_factor3"):
                listener.enterExp_factor3(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExp_factor3"):
                listener.exitExp_factor3(self)




    def exp_factor3(self):

        localctx = MySQLParser.Exp_factor3Context(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_exp_factor3)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 425
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,45,self._ctx)
            if la_ == 1:
                self.state = 424
                self.match(MySQLParser.NOT_SYM)


            self.state = 427
            self.exp_factor4()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Exp_factor4Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Exp_factor4Context, self).__init__(parent, invokingState)
            self.parser = parser

        def bool_primary(self):
            return self.getTypedRuleContext(MySQLParser.Bool_primaryContext,0)


        def IS_SYM(self):
            return self.getToken(MySQLParser.IS_SYM, 0)

        def boolean_literal(self):
            return self.getTypedRuleContext(MySQLParser.Boolean_literalContext,0)


        def NULL_SYM(self):
            return self.getToken(MySQLParser.NULL_SYM, 0)

        def NOT_SYM(self):
            return self.getToken(MySQLParser.NOT_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_exp_factor4

        def enterRule(self, listener):
            if hasattr(listener, "enterExp_factor4"):
                listener.enterExp_factor4(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExp_factor4"):
                listener.exitExp_factor4(self)




    def exp_factor4(self):

        localctx = MySQLParser.Exp_factor4Context(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_exp_factor4)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 429
            self.bool_primary()
            self.state = 438
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,48,self._ctx)
            if la_ == 1:
                self.state = 430
                self.match(MySQLParser.IS_SYM)
                self.state = 432
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.NOT_SYM:
                    self.state = 431
                    self.match(MySQLParser.NOT_SYM)


                self.state = 436
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [MySQLParser.FALSE_SYM, MySQLParser.TRUE_SYM]:
                    self.state = 434
                    self.boolean_literal()
                    pass
                elif token in [MySQLParser.NULL_SYM]:
                    self.state = 435
                    self.match(MySQLParser.NULL_SYM)
                    pass
                else:
                    raise NoViableAltException(self)



        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.ExpressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def exp_factor1(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Exp_factor1Context)
            else:
                return self.getTypedRuleContext(MySQLParser.Exp_factor1Context,i)


        def OR_SYM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.OR_SYM)
            else:
                return self.getToken(MySQLParser.OR_SYM, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterExpression"):
                listener.enterExpression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExpression"):
                listener.exitExpression(self)




    def expression(self):

        localctx = MySQLParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 440
            self.exp_factor1()
            self.state = 445
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,49,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 441
                    self.match(MySQLParser.OR_SYM)
                    self.state = 442
                    self.exp_factor1() 
                self.state = 447
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,49,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Expression_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Expression_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(MySQLParser.LPAREN, 0)

        def expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(MySQLParser.ExpressionContext,i)


        def RPAREN(self):
            return self.getToken(MySQLParser.RPAREN, 0)

        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.COMMA)
            else:
                return self.getToken(MySQLParser.COMMA, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_expression_list

        def enterRule(self, listener):
            if hasattr(listener, "enterExpression_list"):
                listener.enterExpression_list(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExpression_list"):
                listener.exitExpression_list(self)




    def expression_list(self):

        localctx = MySQLParser.Expression_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_expression_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 448
            self.match(MySQLParser.LPAREN)
            self.state = 449
            self.expression()
            self.state = 454
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MySQLParser.COMMA:
                self.state = 450
                self.match(MySQLParser.COMMA)
                self.state = 451
                self.expression()
                self.state = 456
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 457
            self.match(MySQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Factor1Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Factor1Context, self).__init__(parent, invokingState)
            self.parser = parser

        def factor2(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Factor2Context)
            else:
                return self.getTypedRuleContext(MySQLParser.Factor2Context,i)


        def BITAND(self):
            return self.getToken(MySQLParser.BITAND, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_factor1

        def enterRule(self, listener):
            if hasattr(listener, "enterFactor1"):
                listener.enterFactor1(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFactor1"):
                listener.exitFactor1(self)




    def factor1(self):

        localctx = MySQLParser.Factor1Context(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_factor1)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 459
            self.factor2()
            self.state = 462
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,51,self._ctx)
            if la_ == 1:
                self.state = 460
                self.match(MySQLParser.BITAND)
                self.state = 461
                self.factor2()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Factor2Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Factor2Context, self).__init__(parent, invokingState)
            self.parser = parser

        def factor3(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Factor3Context)
            else:
                return self.getTypedRuleContext(MySQLParser.Factor3Context,i)


        def SHIFT_LEFT(self):
            return self.getToken(MySQLParser.SHIFT_LEFT, 0)

        def SHIFT_RIGHT(self):
            return self.getToken(MySQLParser.SHIFT_RIGHT, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_factor2

        def enterRule(self, listener):
            if hasattr(listener, "enterFactor2"):
                listener.enterFactor2(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFactor2"):
                listener.exitFactor2(self)




    def factor2(self):

        localctx = MySQLParser.Factor2Context(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_factor2)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 464
            self.factor3()
            self.state = 467
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,52,self._ctx)
            if la_ == 1:
                self.state = 465
                _la = self._input.LA(1)
                if not(_la==MySQLParser.SHIFT_LEFT or _la==MySQLParser.SHIFT_RIGHT):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 466
                self.factor3()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Factor3Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Factor3Context, self).__init__(parent, invokingState)
            self.parser = parser

        def factor4(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Factor4Context)
            else:
                return self.getTypedRuleContext(MySQLParser.Factor4Context,i)


        def PLUS(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.PLUS)
            else:
                return self.getToken(MySQLParser.PLUS, i)

        def MINUS(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.MINUS)
            else:
                return self.getToken(MySQLParser.MINUS, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_factor3

        def enterRule(self, listener):
            if hasattr(listener, "enterFactor3"):
                listener.enterFactor3(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFactor3"):
                listener.exitFactor3(self)




    def factor3(self):

        localctx = MySQLParser.Factor3Context(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_factor3)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 469
            self.factor4()
            self.state = 474
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,53,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 470
                    _la = self._input.LA(1)
                    if not(_la==MySQLParser.PLUS or _la==MySQLParser.MINUS):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 471
                    self.factor4() 
                self.state = 476
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,53,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Factor4Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Factor4Context, self).__init__(parent, invokingState)
            self.parser = parser

        def factor5(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Factor5Context)
            else:
                return self.getTypedRuleContext(MySQLParser.Factor5Context,i)


        def ASTERISK(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.ASTERISK)
            else:
                return self.getToken(MySQLParser.ASTERISK, i)

        def DIVIDE(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.DIVIDE)
            else:
                return self.getToken(MySQLParser.DIVIDE, i)

        def MOD_SYM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.MOD_SYM)
            else:
                return self.getToken(MySQLParser.MOD_SYM, i)

        def POWER_OP(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.POWER_OP)
            else:
                return self.getToken(MySQLParser.POWER_OP, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_factor4

        def enterRule(self, listener):
            if hasattr(listener, "enterFactor4"):
                listener.enterFactor4(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFactor4"):
                listener.exitFactor4(self)




    def factor4(self):

        localctx = MySQLParser.Factor4Context(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_factor4)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 477
            self.factor5()
            self.state = 482
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,54,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 478
                    _la = self._input.LA(1)
                    if not(((((_la - 603)) & ~0x3f) == 0 and ((1 << (_la - 603)) & ((1 << (MySQLParser.DIVIDE - 603)) | (1 << (MySQLParser.MOD_SYM - 603)) | (1 << (MySQLParser.ASTERISK - 603)) | (1 << (MySQLParser.POWER_OP - 603)))) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 479
                    self.factor5() 
                self.state = 484
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,54,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Factor5Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Factor5Context, self).__init__(parent, invokingState)
            self.parser = parser

        def simple_expr(self):
            return self.getTypedRuleContext(MySQLParser.Simple_exprContext,0)


        def interval_expr(self):
            return self.getTypedRuleContext(MySQLParser.Interval_exprContext,0)


        def PLUS(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.PLUS)
            else:
                return self.getToken(MySQLParser.PLUS, i)

        def MINUS(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.MINUS)
            else:
                return self.getToken(MySQLParser.MINUS, i)

        def NEGATION(self):
            return self.getToken(MySQLParser.NEGATION, 0)

        def BINARY(self):
            return self.getToken(MySQLParser.BINARY, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_factor5

        def enterRule(self, listener):
            if hasattr(listener, "enterFactor5"):
                listener.enterFactor5(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFactor5"):
                listener.exitFactor5(self)




    def factor5(self):

        localctx = MySQLParser.Factor5Context(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_factor5)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 486
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,55,self._ctx)
            if la_ == 1:
                self.state = 485
                _la = self._input.LA(1)
                if not(_la==MySQLParser.BINARY or ((((_la - 624)) & ~0x3f) == 0 and ((1 << (_la - 624)) & ((1 << (MySQLParser.PLUS - 624)) | (1 << (MySQLParser.MINUS - 624)) | (1 << (MySQLParser.NEGATION - 624)))) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


            self.state = 488
            self.simple_expr()
            self.state = 491
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,56,self._ctx)
            if la_ == 1:
                self.state = 489
                _la = self._input.LA(1)
                if not(_la==MySQLParser.PLUS or _la==MySQLParser.MINUS):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 490
                self.interval_expr()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Function_callContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Function_callContext, self).__init__(parent, invokingState)
            self.parser = parser

        def functionList(self):
            return self.getTypedRuleContext(MySQLParser.FunctionListContext,0)


        def LPAREN(self):
            return self.getToken(MySQLParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(MySQLParser.RPAREN, 0)

        def expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(MySQLParser.ExpressionContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.COMMA)
            else:
                return self.getToken(MySQLParser.COMMA, i)

        def CONVERT_SYM(self):
            return self.getToken(MySQLParser.CONVERT_SYM, 0)

        def cast_data_type(self):
            return self.getTypedRuleContext(MySQLParser.Cast_data_typeContext,0)


        def USING_SYM(self):
            return self.getToken(MySQLParser.USING_SYM, 0)

        def transcoding_name(self):
            return self.getTypedRuleContext(MySQLParser.Transcoding_nameContext,0)


        def CAST_SYM(self):
            return self.getToken(MySQLParser.CAST_SYM, 0)

        def AS_SYM(self):
            return self.getToken(MySQLParser.AS_SYM, 0)

        def group_functions(self):
            return self.getTypedRuleContext(MySQLParser.Group_functionsContext,0)


        def bit_expr(self):
            return self.getTypedRuleContext(MySQLParser.Bit_exprContext,0)


        def ASTERISK(self):
            return self.getToken(MySQLParser.ASTERISK, 0)

        def ALL(self):
            return self.getToken(MySQLParser.ALL, 0)

        def DISTINCT(self):
            return self.getToken(MySQLParser.DISTINCT, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_function_call

        def enterRule(self, listener):
            if hasattr(listener, "enterFunction_call"):
                listener.enterFunction_call(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFunction_call"):
                listener.exitFunction_call(self)




    def function_call(self):

        localctx = MySQLParser.Function_callContext(self, self._ctx, self.state)
        self.enterRule(localctx, 82, self.RULE_function_call)
        self._la = 0 # Token type
        try:
            self.state = 539
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,62,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 493
                self.functionList()
                self.state = 506
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.LPAREN:
                    self.state = 494
                    self.match(MySQLParser.LPAREN)
                    self.state = 503
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << MySQLParser.ABS) | (1 << MySQLParser.ACOS) | (1 << MySQLParser.ADDDATE) | (1 << MySQLParser.ADDTIME) | (1 << MySQLParser.AES_DECRYPT) | (1 << MySQLParser.AES_ENCRYPT) | (1 << MySQLParser.ASCII_SYM) | (1 << MySQLParser.ASIN) | (1 << MySQLParser.ATAN) | (1 << MySQLParser.ATAN2) | (1 << MySQLParser.AVG) | (1 << MySQLParser.BENCHMARK) | (1 << MySQLParser.BIN) | (1 << MySQLParser.BINARY) | (1 << MySQLParser.BIT_AND) | (1 << MySQLParser.BIT_COUNT) | (1 << MySQLParser.BIT_LENGTH) | (1 << MySQLParser.BIT_OR) | (1 << MySQLParser.BIT_XOR) | (1 << MySQLParser.CASE_SYM) | (1 << MySQLParser.CAST_SYM) | (1 << MySQLParser.CEIL) | (1 << MySQLParser.CEILING) | (1 << MySQLParser.CHAR) | (1 << MySQLParser.CHARSET) | (1 << MySQLParser.CHAR_LENGTH) | (1 << MySQLParser.COERCIBILITY) | (1 << MySQLParser.COLLATION) | (1 << MySQLParser.CONCAT) | (1 << MySQLParser.CONCAT_WS) | (1 << MySQLParser.CONNECTION_ID) | (1 << MySQLParser.CONV) | (1 << MySQLParser.CONVERT_SYM) | (1 << MySQLParser.CONVERT_TZ) | (1 << MySQLParser.COS) | (1 << MySQLParser.COT) | (1 << MySQLParser.COUNT) | (1 << MySQLParser.CRC32) | (1 << MySQLParser.CURDATE) | (1 << MySQLParser.CURRENT_USER) | (1 << MySQLParser.CURTIME))) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & ((1 << (MySQLParser.DATABASE - 64)) | (1 << (MySQLParser.DATEDIFF - 64)) | (1 << (MySQLParser.DATE_ADD - 64)) | (1 << (MySQLParser.DATE_FORMAT - 64)) | (1 << (MySQLParser.DATE_SUB - 64)) | (1 << (MySQLParser.DATE_SYM - 64)) | (1 << (MySQLParser.DAYNAME - 64)) | (1 << (MySQLParser.DAYOFMONTH - 64)) | (1 << (MySQLParser.DAYOFWEEK - 64)) | (1 << (MySQLParser.DAYOFYEAR - 64)) | (1 << (MySQLParser.DECODE - 64)) | (1 << (MySQLParser.DEFAULT - 64)) | (1 << (MySQLParser.DEGREES - 64)) | (1 << (MySQLParser.DES_DECRYPT - 64)) | (1 << (MySQLParser.DES_ENCRYPT - 64)) | (1 << (MySQLParser.ELT - 64)) | (1 << (MySQLParser.ENCODE - 64)) | (1 << (MySQLParser.ENCRYPT - 64)) | (1 << (MySQLParser.EXISTS - 64)) | (1 << (MySQLParser.EXP - 64)) | (1 << (MySQLParser.EXPORT_SET - 64)) | (1 << (MySQLParser.EXTRACT - 64)) | (1 << (MySQLParser.FALSE_SYM - 64)) | (1 << (MySQLParser.FIELD - 64)) | (1 << (MySQLParser.FIND_IN_SET - 64)) | (1 << (MySQLParser.FLOOR - 64)) | (1 << (MySQLParser.FORMAT - 64)) | (1 << (MySQLParser.FOUND_ROWS - 64)) | (1 << (MySQLParser.FROM_BASE64 - 64)) | (1 << (MySQLParser.FROM_DAYS - 64)) | (1 << (MySQLParser.FROM_UNIXTIME - 64)) | (1 << (MySQLParser.GET_FORMAT - 64)) | (1 << (MySQLParser.GET_LOCK - 64)) | (1 << (MySQLParser.GROUP_CONCAT - 64)) | (1 << (MySQLParser.HEX - 64)) | (1 << (MySQLParser.HOUR - 64)))) != 0) or ((((_la - 132)) & ~0x3f) == 0 and ((1 << (_la - 132)) & ((1 << (MySQLParser.IF - 132)) | (1 << (MySQLParser.IFNULL - 132)) | (1 << (MySQLParser.INET_ATON - 132)) | (1 << (MySQLParser.INET_NTOA - 132)) | (1 << (MySQLParser.INSERT - 132)) | (1 << (MySQLParser.INSTR - 132)) | (1 << (MySQLParser.INTERVAL_SYM - 132)) | (1 << (MySQLParser.IS_FREE_LOCK - 132)) | (1 << (MySQLParser.IS_USED_LOCK - 132)) | (1 << (MySQLParser.LAST_DAY - 132)) | (1 << (MySQLParser.LAST_INSERT_ID - 132)) | (1 << (MySQLParser.LEFT - 132)) | (1 << (MySQLParser.LENGTH - 132)) | (1 << (MySQLParser.LN - 132)) | (1 << (MySQLParser.LOAD_FILE - 132)) | (1 << (MySQLParser.LOCATE - 132)) | (1 << (MySQLParser.LOG - 132)) | (1 << (MySQLParser.LOG10 - 132)) | (1 << (MySQLParser.LOG2 - 132)) | (1 << (MySQLParser.LOWER - 132)) | (1 << (MySQLParser.LPAD - 132)) | (1 << (MySQLParser.LTRIM - 132)) | (1 << (MySQLParser.MAKEDATE - 132)) | (1 << (MySQLParser.MAKETIME - 132)) | (1 << (MySQLParser.MAKE_SET - 132)) | (1 << (MySQLParser.MASTER_POS_WAIT - 132)) | (1 << (MySQLParser.MATCH - 132)) | (1 << (MySQLParser.MAX_SYM - 132)) | (1 << (MySQLParser.MD5 - 132)) | (1 << (MySQLParser.MICROSECOND - 132)) | (1 << (MySQLParser.MID - 132)) | (1 << (MySQLParser.MINUTE - 132)) | (1 << (MySQLParser.MIN_SYM - 132)) | (1 << (MySQLParser.MOD - 132)) | (1 << (MySQLParser.MONTH - 132)) | (1 << (MySQLParser.MONTHNAME - 132)) | (1 << (MySQLParser.NAME_CONST - 132)))) != 0) or ((((_la - 197)) & ~0x3f) == 0 and ((1 << (_la - 197)) & ((1 << (MySQLParser.NOT_SYM - 197)) | (1 << (MySQLParser.NOW - 197)) | (1 << (MySQLParser.NULL_SYM - 197)) | (1 << (MySQLParser.OCT - 197)) | (1 << (MySQLParser.OLD_PASSWORD - 197)) | (1 << (MySQLParser.ORD - 197)) | (1 << (MySQLParser.PASSWORD - 197)) | (1 << (MySQLParser.PERIOD_ADD - 197)) | (1 << (MySQLParser.PERIOD_DIFF - 197)) | (1 << (MySQLParser.PI - 197)) | (1 << (MySQLParser.POW - 197)) | (1 << (MySQLParser.POWER - 197)) | (1 << (MySQLParser.QUARTER - 197)) | (1 << (MySQLParser.QUOTE - 197)) | (1 << (MySQLParser.RADIANS - 197)) | (1 << (MySQLParser.RAND - 197)) | (1 << (MySQLParser.RELEASE_LOCK - 197)) | (1 << (MySQLParser.REPEAT - 197)) | (1 << (MySQLParser.REPLACE - 197)) | (1 << (MySQLParser.REVERSE - 197)) | (1 << (MySQLParser.RIGHT - 197)) | (1 << (MySQLParser.ROUND - 197)) | (1 << (MySQLParser.ROW_SYM - 197)) | (1 << (MySQLParser.RPAD - 197)) | (1 << (MySQLParser.RTRIM - 197)) | (1 << (MySQLParser.SCHEMA - 197)) | (1 << (MySQLParser.SECOND - 197)) | (1 << (MySQLParser.SEC_TO_TIME - 197)) | (1 << (MySQLParser.SESSION_USER - 197)) | (1 << (MySQLParser.SIGN - 197)) | (1 << (MySQLParser.SIN - 197)) | (1 << (MySQLParser.SLEEP - 197)) | (1 << (MySQLParser.SOUNDEX - 197)) | (1 << (MySQLParser.SPACE - 197)) | (1 << (MySQLParser.SQRT - 197)) | (1 << (MySQLParser.STD - 197)) | (1 << (MySQLParser.STDDEV - 197)) | (1 << (MySQLParser.STDDEV_POP - 197)) | (1 << (MySQLParser.STDDEV_SAMP - 197)) | (1 << (MySQLParser.STRCMP - 197)))) != 0) or ((((_la - 261)) & ~0x3f) == 0 and ((1 << (_la - 261)) & ((1 << (MySQLParser.STR_TO_DATE - 261)) | (1 << (MySQLParser.SUBSTRING - 261)) | (1 << (MySQLParser.SUBSTRING_INDEX - 261)) | (1 << (MySQLParser.SUBTIME - 261)) | (1 << (MySQLParser.SUM - 261)) | (1 << (MySQLParser.SYSDATE - 261)) | (1 << (MySQLParser.SYSTEM_USER - 261)) | (1 << (MySQLParser.TAN - 261)) | (1 << (MySQLParser.TIMEDIFF - 261)) | (1 << (MySQLParser.TIMESTAMP - 261)) | (1 << (MySQLParser.TIMESTAMPADD - 261)) | (1 << (MySQLParser.TIMESTAMPDIFF - 261)) | (1 << (MySQLParser.TIME_FORMAT - 261)) | (1 << (MySQLParser.TIME_SYM - 261)) | (1 << (MySQLParser.TIME_TO_SEC - 261)) | (1 << (MySQLParser.TO_BASE64 - 261)) | (1 << (MySQLParser.TO_DAYS - 261)) | (1 << (MySQLParser.TO_SECONDS - 261)) | (1 << (MySQLParser.TRIM - 261)) | (1 << (MySQLParser.TRUE_SYM - 261)) | (1 << (MySQLParser.TRUNCATE - 261)) | (1 << (MySQLParser.UNHEX - 261)) | (1 << (MySQLParser.UNIX_TIMESTAMP - 261)) | (1 << (MySQLParser.UPPER - 261)) | (1 << (MySQLParser.USER - 261)) | (1 << (MySQLParser.UTC_DATE - 261)) | (1 << (MySQLParser.UTC_TIME - 261)) | (1 << (MySQLParser.UTC_TIMESTAMP - 261)) | (1 << (MySQLParser.UUID - 261)) | (1 << (MySQLParser.VALUES - 261)) | (1 << (MySQLParser.VARIANCE - 261)) | (1 << (MySQLParser.VAR_POP - 261)) | (1 << (MySQLParser.VAR_SAMP - 261)) | (1 << (MySQLParser.VERSION_SYM - 261)) | (1 << (MySQLParser.WEEK - 261)) | (1 << (MySQLParser.WEEKDAY - 261)) | (1 << (MySQLParser.WEEKOFYEAR - 261)) | (1 << (MySQLParser.WEIGHT_STRING - 261)) | (1 << (MySQLParser.YEAR - 261)) | (1 << (MySQLParser.YEARWEEK - 261)) | (1 << (MySQLParser.SDIST - 261)) | (1 << (MySQLParser.SAREA - 261)) | (1 << (MySQLParser.SCENTER - 261)) | (1 << (MySQLParser.SCIRCUM - 261)) | (1 << (MySQLParser.SLENGTH - 261)) | (1 << (MySQLParser.SSWAP - 261)) | (1 << (MySQLParser.SNPOINTS - 261)))) != 0) or ((((_la - 325)) & ~0x3f) == 0 and ((1 << (_la - 325)) & ((1 << (MySQLParser.SSTR - 325)) | (1 << (MySQLParser.MYSQL_SPHERE_VERSION - 325)) | (1 << (MySQLParser.SRCONTAINSL - 325)) | (1 << (MySQLParser.SLCONTAINSR - 325)) | (1 << (MySQLParser.SRNOTCONTAINSL - 325)) | (1 << (MySQLParser.SLNOTCONTAINSR - 325)) | (1 << (MySQLParser.SOVERLAPS - 325)) | (1 << (MySQLParser.SNOTOVERLAPS - 325)) | (1 << (MySQLParser.SEQUAL - 325)) | (1 << (MySQLParser.SNOTEQUAL - 325)) | (1 << (MySQLParser.STRANSFORM - 325)) | (1 << (MySQLParser.SINVERSE - 325)) | (1 << (MySQLParser.SPOINT - 325)) | (1 << (MySQLParser.SPOINT_LONG - 325)) | (1 << (MySQLParser.SPOINT_LAT - 325)) | (1 << (MySQLParser.SPOINT_X - 325)) | (1 << (MySQLParser.SPOINT_Y - 325)) | (1 << (MySQLParser.SPOINT_Z - 325)) | (1 << (MySQLParser.SPOINT_EQUAL - 325)) | (1 << (MySQLParser.STRANS - 325)) | (1 << (MySQLParser.STRANS_POINT - 325)) | (1 << (MySQLParser.STRANS_POINT_INVERSE - 325)) | (1 << (MySQLParser.STRANS_EQUAL - 325)) | (1 << (MySQLParser.STRANS_EQUAL_NEG - 325)) | (1 << (MySQLParser.STRANS_PHI - 325)) | (1 << (MySQLParser.STRANS_THETA - 325)) | (1 << (MySQLParser.STRANS_PSI - 325)) | (1 << (MySQLParser.STRANS_AXES - 325)) | (1 << (MySQLParser.STRANS_INVERT - 325)) | (1 << (MySQLParser.STRANS_ZXZ - 325)) | (1 << (MySQLParser.STRANS_TRANS - 325)) | (1 << (MySQLParser.STRANS_TRANS_INV - 325)) | (1 << (MySQLParser.SCIRCLE - 325)) | (1 << (MySQLParser.SCIRCLE_RADIUS - 325)) | (1 << (MySQLParser.SCIRCLE_EQUAL - 325)) | (1 << (MySQLParser.SCIRCLE_EQUAL_NEG - 325)) | (1 << (MySQLParser.SCIRCLE_OVERLAP - 325)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_NEG - 325)) | (1 << (MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE - 325)) | (1 << (MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE_NEG - 325)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_CIRCLE - 325)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_CIRCLE_NEG - 325)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE - 325)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_NEG - 325)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM - 325)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM_NEG - 325)) | (1 << (MySQLParser.STRANS_CIRCLE - 325)) | (1 << (MySQLParser.STRANS_CIRCLE_INVERSE - 325)) | (1 << (MySQLParser.SLINE - 325)) | (1 << (MySQLParser.SMERIDIAN - 325)) | (1 << (MySQLParser.SLINE_BEG - 325)) | (1 << (MySQLParser.SLINE_END - 325)) | (1 << (MySQLParser.SLINE_EQUAL - 325)) | (1 << (MySQLParser.SLINE_EQUAL_NEG - 325)) | (1 << (MySQLParser.SLINE_TURN - 325)) | (1 << (MySQLParser.SLINE_CROSSES - 325)) | (1 << (MySQLParser.SLINE_CROSSES_NEG - 325)) | (1 << (MySQLParser.SLINE_OVERLAP - 325)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT - 325)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT_COM - 325)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT_NEG - 325)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT_COM_NEG - 325)) | (1 << (MySQLParser.STRANS_LINE - 325)) | (1 << (MySQLParser.STRANS_LINE_INVERSE - 325)))) != 0) or ((((_la - 389)) & ~0x3f) == 0 and ((1 << (_la - 389)) & ((1 << (MySQLParser.SLINE_OVERLAP_CIRCLE - 389)) | (1 << (MySQLParser.SLINE_OVERLAP_CIRCLE_COM - 389)) | (1 << (MySQLParser.SLINE_OVERLAP_CIRCLE_NEG - 389)) | (1 << (MySQLParser.SLINE_OVERLAP_CIRCLE_COM_NEG - 389)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE - 389)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE_COM - 389)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE_NEG - 389)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE_COM_NEG - 389)) | (1 << (MySQLParser.SELLIPSE - 389)) | (1 << (MySQLParser.SELLIPSE_INC - 389)) | (1 << (MySQLParser.SELLIPSE_LRAD - 389)) | (1 << (MySQLParser.SELLIPSE_SRAD - 389)) | (1 << (MySQLParser.SELLIPSE_EQUAL - 389)) | (1 << (MySQLParser.SELLIPSE_EQUAL_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_ELLIPSE - 389)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_ELLIPSE_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT_COM - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT_COM_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM_NEG - 389)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE - 389)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_NEG - 389)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM - 389)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE - 389)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM - 389)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE - 389)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE_COM - 389)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE_COM_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE_NEG - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE_COM - 389)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE_COM_NEG - 389)) | (1 << (MySQLParser.STRANS_ELLIPSE - 389)) | (1 << (MySQLParser.STRANS_ELLIPSE_INVERSE - 389)) | (1 << (MySQLParser.SPOLY - 389)) | (1 << (MySQLParser.SPOLY_EQUAL - 389)) | (1 << (MySQLParser.SPOLY_EQUAL_NEG - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON_NEG - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON_COM - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON_COM_NEG - 389)) | (1 << (MySQLParser.SPOLY_OVERLAP_POLYGON - 389)) | (1 << (MySQLParser.SPOLY_OVERLAP_POLYGON_NEG - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_POINT - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_POINT_NEG - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_POINT_COM - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_POINT_COM_NEG - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE_NEG - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE_COM - 389)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE_COM_NEG - 389)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON - 389)))) != 0) or ((((_la - 453)) & ~0x3f) == 0 and ((1 << (_la - 453)) & ((1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON_NEG - 453)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM - 453)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM_NEG - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE_NEG - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE_COM - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE_COM_NEG - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE_NEG - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE_COM - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE_COM_NEG - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE_NEG - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE_COM - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE_COM_NEG - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE_NEG - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM_NEG - 453)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON - 453)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON_NEG - 453)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM - 453)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM_NEG - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE_NEG - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM - 453)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM_NEG - 453)) | (1 << (MySQLParser.STRANS_POLY - 453)) | (1 << (MySQLParser.STRANS_POLY_INVERSE - 453)) | (1 << (MySQLParser.SPOLY_ADD_POINT_AGGR - 453)) | (1 << (MySQLParser.SPOLY_AGGR - 453)) | (1 << (MySQLParser.SPATH - 453)) | (1 << (MySQLParser.SPATH_EQUAL - 453)) | (1 << (MySQLParser.SPATH_EQUAL_NEG - 453)) | (1 << (MySQLParser.SPATH_OVERLAP_PATH - 453)) | (1 << (MySQLParser.SPATH_OVERLAP_PATH_NEG - 453)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT - 453)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT_NEG - 453)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT_COM - 453)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT_COM_NEG - 453)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH - 453)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH_NEG - 453)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH_COM - 453)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH_COM_NEG - 453)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH - 453)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH_NEG - 453)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH_COM - 453)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH_COM_NEG - 453)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE - 453)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE_NEG - 453)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE_COM - 453)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE_COM_NEG - 453)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH - 453)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH_NEG - 453)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH_COM - 453)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH_COM_NEG - 453)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_PATH - 453)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_PATH_NEG - 453)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_PATH_COM - 453)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_PATH_COM_NEG - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH_NEG - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH_COM - 453)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH_COM_NEG - 453)))) != 0) or ((((_la - 517)) & ~0x3f) == 0 and ((1 << (_la - 517)) & ((1 << (MySQLParser.SPOLY_OVERLAP_PATH - 517)) | (1 << (MySQLParser.SPOLY_OVERLAP_PATH_NEG - 517)) | (1 << (MySQLParser.SPOLY_OVERLAP_PATH_COM - 517)) | (1 << (MySQLParser.SPOLY_OVERLAP_PATH_COM_NEG - 517)) | (1 << (MySQLParser.STRANS_PATH - 517)) | (1 << (MySQLParser.STRANS_PATH_INVERSE - 517)) | (1 << (MySQLParser.SPATH_ADD_POINT_AGGR - 517)) | (1 << (MySQLParser.SPATH_AGGR - 517)) | (1 << (MySQLParser.SBOX - 517)) | (1 << (MySQLParser.SBOX_SW - 517)) | (1 << (MySQLParser.SBOX_SE - 517)) | (1 << (MySQLParser.SBOX_NW - 517)) | (1 << (MySQLParser.SBOX_NE - 517)) | (1 << (MySQLParser.SBOX_EQUAL - 517)) | (1 << (MySQLParser.SBOX_EQUAL_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX_COM - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX_COM_NEG - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_BOX - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_BOX_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT_COM - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT_COM_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE_COM - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE_COM_NEG - 517)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX - 517)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX_NEG - 517)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX_COM - 517)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX_COM_NEG - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE_NEG - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE_COM - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE_COM_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE_COM - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE_COM_NEG - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE_NEG - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE_COM - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE_COM_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE_COM - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE_COM_NEG - 517)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX - 517)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX_NEG - 517)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX_COM - 517)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX_COM_NEG - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE_NEG - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE_COM - 517)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE_COM_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_POLY - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_POLY_NEG - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_POLY_COM - 517)) | (1 << (MySQLParser.SBOX_CONTAINS_POLY_COM_NEG - 517)) | (1 << (MySQLParser.SPOLY_CONTAINS_BOX - 517)) | (1 << (MySQLParser.SPOLY_CONTAINS_BOX_NEG - 517)) | (1 << (MySQLParser.SPOLY_CONTAINS_BOX_COM - 517)))) != 0) or ((((_la - 581)) & ~0x3f) == 0 and ((1 << (_la - 581)) & ((1 << (MySQLParser.SPOLY_CONTAINS_BOX_COM_NEG - 581)) | (1 << (MySQLParser.SBOX_OVERLAP_POLY - 581)) | (1 << (MySQLParser.SBOX_OVERLAP_POLY_NEG - 581)) | (1 << (MySQLParser.SBOX_OVERLAP_POLY_COM - 581)) | (1 << (MySQLParser.SBOX_OVERLAP_POLY_COM_NEG - 581)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH - 581)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH_NEG - 581)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH_COM - 581)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH_COM_NEG - 581)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH - 581)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH_NEG - 581)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH_COM - 581)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH_COM_NEG - 581)) | (1 << (MySQLParser.STRRPOS - 581)) | (1 << (MySQLParser.IDLE - 581)) | (1 << (MySQLParser.ANGDIST - 581)) | (1 << (MySQLParser.HILBERTKEY - 581)) | (1 << (MySQLParser.COORDFROMHILBERTKEY - 581)) | (1 << (MySQLParser.SUM_OF_SQUARES - 581)) | (1 << (MySQLParser.PARTITADD_SUM_OF_SQARES - 581)) | (1 << (MySQLParser.GAIA_HEALPIX - 581)) | (1 << (MySQLParser.LPAREN - 581)) | (1 << (MySQLParser.PLUS - 581)) | (1 << (MySQLParser.MINUS - 581)) | (1 << (MySQLParser.NEGATION - 581)) | (1 << (MySQLParser.INTEGER_NUM - 581)) | (1 << (MySQLParser.HEX_DIGIT - 581)) | (1 << (MySQLParser.BIT_NUM - 581)) | (1 << (MySQLParser.REAL_NUMBER - 581)) | (1 << (MySQLParser.TEXT_STRING - 581)) | (1 << (MySQLParser.ID - 581)) | (1 << (MySQLParser.USER_VAR - 581)))) != 0):
                        self.state = 495
                        self.expression()
                        self.state = 500
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        while _la==MySQLParser.COMMA:
                            self.state = 496
                            self.match(MySQLParser.COMMA)
                            self.state = 497
                            self.expression()
                            self.state = 502
                            self._errHandler.sync(self)
                            _la = self._input.LA(1)



                    self.state = 505
                    self.match(MySQLParser.RPAREN)


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 508
                self.match(MySQLParser.CONVERT_SYM)
                self.state = 509
                self.match(MySQLParser.LPAREN)
                self.state = 510
                self.expression()
                self.state = 511
                self.match(MySQLParser.COMMA)
                self.state = 512
                self.cast_data_type()
                self.state = 513
                self.match(MySQLParser.RPAREN)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 515
                self.match(MySQLParser.CONVERT_SYM)
                self.state = 516
                self.match(MySQLParser.LPAREN)
                self.state = 517
                self.expression()
                self.state = 518
                self.match(MySQLParser.USING_SYM)
                self.state = 519
                self.transcoding_name()
                self.state = 520
                self.match(MySQLParser.RPAREN)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 522
                self.match(MySQLParser.CAST_SYM)
                self.state = 523
                self.match(MySQLParser.LPAREN)
                self.state = 524
                self.expression()
                self.state = 525
                self.match(MySQLParser.AS_SYM)
                self.state = 526
                self.cast_data_type()
                self.state = 527
                self.match(MySQLParser.RPAREN)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 529
                self.group_functions()
                self.state = 530
                self.match(MySQLParser.LPAREN)
                self.state = 532
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.ALL or _la==MySQLParser.DISTINCT or _la==MySQLParser.ASTERISK:
                    self.state = 531
                    _la = self._input.LA(1)
                    if not(_la==MySQLParser.ALL or _la==MySQLParser.DISTINCT or _la==MySQLParser.ASTERISK):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()


                self.state = 535
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << MySQLParser.ABS) | (1 << MySQLParser.ACOS) | (1 << MySQLParser.ADDDATE) | (1 << MySQLParser.ADDTIME) | (1 << MySQLParser.AES_DECRYPT) | (1 << MySQLParser.AES_ENCRYPT) | (1 << MySQLParser.ASCII_SYM) | (1 << MySQLParser.ASIN) | (1 << MySQLParser.ATAN) | (1 << MySQLParser.ATAN2) | (1 << MySQLParser.AVG) | (1 << MySQLParser.BENCHMARK) | (1 << MySQLParser.BIN) | (1 << MySQLParser.BINARY) | (1 << MySQLParser.BIT_AND) | (1 << MySQLParser.BIT_COUNT) | (1 << MySQLParser.BIT_LENGTH) | (1 << MySQLParser.BIT_OR) | (1 << MySQLParser.BIT_XOR) | (1 << MySQLParser.CASE_SYM) | (1 << MySQLParser.CAST_SYM) | (1 << MySQLParser.CEIL) | (1 << MySQLParser.CEILING) | (1 << MySQLParser.CHAR) | (1 << MySQLParser.CHARSET) | (1 << MySQLParser.CHAR_LENGTH) | (1 << MySQLParser.COERCIBILITY) | (1 << MySQLParser.COLLATION) | (1 << MySQLParser.CONCAT) | (1 << MySQLParser.CONCAT_WS) | (1 << MySQLParser.CONNECTION_ID) | (1 << MySQLParser.CONV) | (1 << MySQLParser.CONVERT_SYM) | (1 << MySQLParser.CONVERT_TZ) | (1 << MySQLParser.COS) | (1 << MySQLParser.COT) | (1 << MySQLParser.COUNT) | (1 << MySQLParser.CRC32) | (1 << MySQLParser.CURDATE) | (1 << MySQLParser.CURRENT_USER) | (1 << MySQLParser.CURTIME))) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & ((1 << (MySQLParser.DATABASE - 64)) | (1 << (MySQLParser.DATEDIFF - 64)) | (1 << (MySQLParser.DATE_ADD - 64)) | (1 << (MySQLParser.DATE_FORMAT - 64)) | (1 << (MySQLParser.DATE_SUB - 64)) | (1 << (MySQLParser.DATE_SYM - 64)) | (1 << (MySQLParser.DAYNAME - 64)) | (1 << (MySQLParser.DAYOFMONTH - 64)) | (1 << (MySQLParser.DAYOFWEEK - 64)) | (1 << (MySQLParser.DAYOFYEAR - 64)) | (1 << (MySQLParser.DECODE - 64)) | (1 << (MySQLParser.DEFAULT - 64)) | (1 << (MySQLParser.DEGREES - 64)) | (1 << (MySQLParser.DES_DECRYPT - 64)) | (1 << (MySQLParser.DES_ENCRYPT - 64)) | (1 << (MySQLParser.ELT - 64)) | (1 << (MySQLParser.ENCODE - 64)) | (1 << (MySQLParser.ENCRYPT - 64)) | (1 << (MySQLParser.EXISTS - 64)) | (1 << (MySQLParser.EXP - 64)) | (1 << (MySQLParser.EXPORT_SET - 64)) | (1 << (MySQLParser.EXTRACT - 64)) | (1 << (MySQLParser.FALSE_SYM - 64)) | (1 << (MySQLParser.FIELD - 64)) | (1 << (MySQLParser.FIND_IN_SET - 64)) | (1 << (MySQLParser.FLOOR - 64)) | (1 << (MySQLParser.FORMAT - 64)) | (1 << (MySQLParser.FOUND_ROWS - 64)) | (1 << (MySQLParser.FROM_BASE64 - 64)) | (1 << (MySQLParser.FROM_DAYS - 64)) | (1 << (MySQLParser.FROM_UNIXTIME - 64)) | (1 << (MySQLParser.GET_FORMAT - 64)) | (1 << (MySQLParser.GET_LOCK - 64)) | (1 << (MySQLParser.GROUP_CONCAT - 64)) | (1 << (MySQLParser.HEX - 64)) | (1 << (MySQLParser.HOUR - 64)))) != 0) or ((((_la - 132)) & ~0x3f) == 0 and ((1 << (_la - 132)) & ((1 << (MySQLParser.IF - 132)) | (1 << (MySQLParser.IFNULL - 132)) | (1 << (MySQLParser.INET_ATON - 132)) | (1 << (MySQLParser.INET_NTOA - 132)) | (1 << (MySQLParser.INSERT - 132)) | (1 << (MySQLParser.INSTR - 132)) | (1 << (MySQLParser.INTERVAL_SYM - 132)) | (1 << (MySQLParser.IS_FREE_LOCK - 132)) | (1 << (MySQLParser.IS_USED_LOCK - 132)) | (1 << (MySQLParser.LAST_DAY - 132)) | (1 << (MySQLParser.LAST_INSERT_ID - 132)) | (1 << (MySQLParser.LEFT - 132)) | (1 << (MySQLParser.LENGTH - 132)) | (1 << (MySQLParser.LN - 132)) | (1 << (MySQLParser.LOAD_FILE - 132)) | (1 << (MySQLParser.LOCATE - 132)) | (1 << (MySQLParser.LOG - 132)) | (1 << (MySQLParser.LOG10 - 132)) | (1 << (MySQLParser.LOG2 - 132)) | (1 << (MySQLParser.LOWER - 132)) | (1 << (MySQLParser.LPAD - 132)) | (1 << (MySQLParser.LTRIM - 132)) | (1 << (MySQLParser.MAKEDATE - 132)) | (1 << (MySQLParser.MAKETIME - 132)) | (1 << (MySQLParser.MAKE_SET - 132)) | (1 << (MySQLParser.MASTER_POS_WAIT - 132)) | (1 << (MySQLParser.MATCH - 132)) | (1 << (MySQLParser.MAX_SYM - 132)) | (1 << (MySQLParser.MD5 - 132)) | (1 << (MySQLParser.MICROSECOND - 132)) | (1 << (MySQLParser.MID - 132)) | (1 << (MySQLParser.MINUTE - 132)) | (1 << (MySQLParser.MIN_SYM - 132)) | (1 << (MySQLParser.MOD - 132)) | (1 << (MySQLParser.MONTH - 132)) | (1 << (MySQLParser.MONTHNAME - 132)) | (1 << (MySQLParser.NAME_CONST - 132)))) != 0) or ((((_la - 198)) & ~0x3f) == 0 and ((1 << (_la - 198)) & ((1 << (MySQLParser.NOW - 198)) | (1 << (MySQLParser.NULL_SYM - 198)) | (1 << (MySQLParser.OCT - 198)) | (1 << (MySQLParser.OLD_PASSWORD - 198)) | (1 << (MySQLParser.ORD - 198)) | (1 << (MySQLParser.PASSWORD - 198)) | (1 << (MySQLParser.PERIOD_ADD - 198)) | (1 << (MySQLParser.PERIOD_DIFF - 198)) | (1 << (MySQLParser.PI - 198)) | (1 << (MySQLParser.POW - 198)) | (1 << (MySQLParser.POWER - 198)) | (1 << (MySQLParser.QUARTER - 198)) | (1 << (MySQLParser.QUOTE - 198)) | (1 << (MySQLParser.RADIANS - 198)) | (1 << (MySQLParser.RAND - 198)) | (1 << (MySQLParser.RELEASE_LOCK - 198)) | (1 << (MySQLParser.REPEAT - 198)) | (1 << (MySQLParser.REPLACE - 198)) | (1 << (MySQLParser.REVERSE - 198)) | (1 << (MySQLParser.RIGHT - 198)) | (1 << (MySQLParser.ROUND - 198)) | (1 << (MySQLParser.ROW_SYM - 198)) | (1 << (MySQLParser.RPAD - 198)) | (1 << (MySQLParser.RTRIM - 198)) | (1 << (MySQLParser.SCHEMA - 198)) | (1 << (MySQLParser.SECOND - 198)) | (1 << (MySQLParser.SEC_TO_TIME - 198)) | (1 << (MySQLParser.SESSION_USER - 198)) | (1 << (MySQLParser.SIGN - 198)) | (1 << (MySQLParser.SIN - 198)) | (1 << (MySQLParser.SLEEP - 198)) | (1 << (MySQLParser.SOUNDEX - 198)) | (1 << (MySQLParser.SPACE - 198)) | (1 << (MySQLParser.SQRT - 198)) | (1 << (MySQLParser.STD - 198)) | (1 << (MySQLParser.STDDEV - 198)) | (1 << (MySQLParser.STDDEV_POP - 198)) | (1 << (MySQLParser.STDDEV_SAMP - 198)) | (1 << (MySQLParser.STRCMP - 198)) | (1 << (MySQLParser.STR_TO_DATE - 198)))) != 0) or ((((_la - 262)) & ~0x3f) == 0 and ((1 << (_la - 262)) & ((1 << (MySQLParser.SUBSTRING - 262)) | (1 << (MySQLParser.SUBSTRING_INDEX - 262)) | (1 << (MySQLParser.SUBTIME - 262)) | (1 << (MySQLParser.SUM - 262)) | (1 << (MySQLParser.SYSDATE - 262)) | (1 << (MySQLParser.SYSTEM_USER - 262)) | (1 << (MySQLParser.TAN - 262)) | (1 << (MySQLParser.TIMEDIFF - 262)) | (1 << (MySQLParser.TIMESTAMP - 262)) | (1 << (MySQLParser.TIMESTAMPADD - 262)) | (1 << (MySQLParser.TIMESTAMPDIFF - 262)) | (1 << (MySQLParser.TIME_FORMAT - 262)) | (1 << (MySQLParser.TIME_SYM - 262)) | (1 << (MySQLParser.TIME_TO_SEC - 262)) | (1 << (MySQLParser.TO_BASE64 - 262)) | (1 << (MySQLParser.TO_DAYS - 262)) | (1 << (MySQLParser.TO_SECONDS - 262)) | (1 << (MySQLParser.TRIM - 262)) | (1 << (MySQLParser.TRUE_SYM - 262)) | (1 << (MySQLParser.TRUNCATE - 262)) | (1 << (MySQLParser.UNHEX - 262)) | (1 << (MySQLParser.UNIX_TIMESTAMP - 262)) | (1 << (MySQLParser.UPPER - 262)) | (1 << (MySQLParser.USER - 262)) | (1 << (MySQLParser.UTC_DATE - 262)) | (1 << (MySQLParser.UTC_TIME - 262)) | (1 << (MySQLParser.UTC_TIMESTAMP - 262)) | (1 << (MySQLParser.UUID - 262)) | (1 << (MySQLParser.VALUES - 262)) | (1 << (MySQLParser.VARIANCE - 262)) | (1 << (MySQLParser.VAR_POP - 262)) | (1 << (MySQLParser.VAR_SAMP - 262)) | (1 << (MySQLParser.VERSION_SYM - 262)) | (1 << (MySQLParser.WEEK - 262)) | (1 << (MySQLParser.WEEKDAY - 262)) | (1 << (MySQLParser.WEEKOFYEAR - 262)) | (1 << (MySQLParser.WEIGHT_STRING - 262)) | (1 << (MySQLParser.YEAR - 262)) | (1 << (MySQLParser.YEARWEEK - 262)) | (1 << (MySQLParser.SDIST - 262)) | (1 << (MySQLParser.SAREA - 262)) | (1 << (MySQLParser.SCENTER - 262)) | (1 << (MySQLParser.SCIRCUM - 262)) | (1 << (MySQLParser.SLENGTH - 262)) | (1 << (MySQLParser.SSWAP - 262)) | (1 << (MySQLParser.SNPOINTS - 262)) | (1 << (MySQLParser.SSTR - 262)))) != 0) or ((((_la - 326)) & ~0x3f) == 0 and ((1 << (_la - 326)) & ((1 << (MySQLParser.MYSQL_SPHERE_VERSION - 326)) | (1 << (MySQLParser.SRCONTAINSL - 326)) | (1 << (MySQLParser.SLCONTAINSR - 326)) | (1 << (MySQLParser.SRNOTCONTAINSL - 326)) | (1 << (MySQLParser.SLNOTCONTAINSR - 326)) | (1 << (MySQLParser.SOVERLAPS - 326)) | (1 << (MySQLParser.SNOTOVERLAPS - 326)) | (1 << (MySQLParser.SEQUAL - 326)) | (1 << (MySQLParser.SNOTEQUAL - 326)) | (1 << (MySQLParser.STRANSFORM - 326)) | (1 << (MySQLParser.SINVERSE - 326)) | (1 << (MySQLParser.SPOINT - 326)) | (1 << (MySQLParser.SPOINT_LONG - 326)) | (1 << (MySQLParser.SPOINT_LAT - 326)) | (1 << (MySQLParser.SPOINT_X - 326)) | (1 << (MySQLParser.SPOINT_Y - 326)) | (1 << (MySQLParser.SPOINT_Z - 326)) | (1 << (MySQLParser.SPOINT_EQUAL - 326)) | (1 << (MySQLParser.STRANS - 326)) | (1 << (MySQLParser.STRANS_POINT - 326)) | (1 << (MySQLParser.STRANS_POINT_INVERSE - 326)) | (1 << (MySQLParser.STRANS_EQUAL - 326)) | (1 << (MySQLParser.STRANS_EQUAL_NEG - 326)) | (1 << (MySQLParser.STRANS_PHI - 326)) | (1 << (MySQLParser.STRANS_THETA - 326)) | (1 << (MySQLParser.STRANS_PSI - 326)) | (1 << (MySQLParser.STRANS_AXES - 326)) | (1 << (MySQLParser.STRANS_INVERT - 326)) | (1 << (MySQLParser.STRANS_ZXZ - 326)) | (1 << (MySQLParser.STRANS_TRANS - 326)) | (1 << (MySQLParser.STRANS_TRANS_INV - 326)) | (1 << (MySQLParser.SCIRCLE - 326)) | (1 << (MySQLParser.SCIRCLE_RADIUS - 326)) | (1 << (MySQLParser.SCIRCLE_EQUAL - 326)) | (1 << (MySQLParser.SCIRCLE_EQUAL_NEG - 326)) | (1 << (MySQLParser.SCIRCLE_OVERLAP - 326)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_NEG - 326)) | (1 << (MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE - 326)) | (1 << (MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE_NEG - 326)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_CIRCLE - 326)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_CIRCLE_NEG - 326)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE - 326)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_NEG - 326)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM - 326)) | (1 << (MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM_NEG - 326)) | (1 << (MySQLParser.STRANS_CIRCLE - 326)) | (1 << (MySQLParser.STRANS_CIRCLE_INVERSE - 326)) | (1 << (MySQLParser.SLINE - 326)) | (1 << (MySQLParser.SMERIDIAN - 326)) | (1 << (MySQLParser.SLINE_BEG - 326)) | (1 << (MySQLParser.SLINE_END - 326)) | (1 << (MySQLParser.SLINE_EQUAL - 326)) | (1 << (MySQLParser.SLINE_EQUAL_NEG - 326)) | (1 << (MySQLParser.SLINE_TURN - 326)) | (1 << (MySQLParser.SLINE_CROSSES - 326)) | (1 << (MySQLParser.SLINE_CROSSES_NEG - 326)) | (1 << (MySQLParser.SLINE_OVERLAP - 326)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT - 326)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT_COM - 326)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT_NEG - 326)) | (1 << (MySQLParser.SLINE_CONTAINS_POINT_COM_NEG - 326)) | (1 << (MySQLParser.STRANS_LINE - 326)) | (1 << (MySQLParser.STRANS_LINE_INVERSE - 326)) | (1 << (MySQLParser.SLINE_OVERLAP_CIRCLE - 326)))) != 0) or ((((_la - 390)) & ~0x3f) == 0 and ((1 << (_la - 390)) & ((1 << (MySQLParser.SLINE_OVERLAP_CIRCLE_COM - 390)) | (1 << (MySQLParser.SLINE_OVERLAP_CIRCLE_NEG - 390)) | (1 << (MySQLParser.SLINE_OVERLAP_CIRCLE_COM_NEG - 390)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE - 390)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE_COM - 390)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE_NEG - 390)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_LINE_COM_NEG - 390)) | (1 << (MySQLParser.SELLIPSE - 390)) | (1 << (MySQLParser.SELLIPSE_INC - 390)) | (1 << (MySQLParser.SELLIPSE_LRAD - 390)) | (1 << (MySQLParser.SELLIPSE_SRAD - 390)) | (1 << (MySQLParser.SELLIPSE_EQUAL - 390)) | (1 << (MySQLParser.SELLIPSE_EQUAL_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_ELLIPSE - 390)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_ELLIPSE_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT_COM - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POINT_COM_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM_NEG - 390)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE - 390)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_NEG - 390)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM - 390)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE - 390)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM - 390)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE - 390)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE_COM - 390)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_LINE_COM_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE_NEG - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE_COM - 390)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_LINE_COM_NEG - 390)) | (1 << (MySQLParser.STRANS_ELLIPSE - 390)) | (1 << (MySQLParser.STRANS_ELLIPSE_INVERSE - 390)) | (1 << (MySQLParser.SPOLY - 390)) | (1 << (MySQLParser.SPOLY_EQUAL - 390)) | (1 << (MySQLParser.SPOLY_EQUAL_NEG - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON_NEG - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON_COM - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_POLYGON_COM_NEG - 390)) | (1 << (MySQLParser.SPOLY_OVERLAP_POLYGON - 390)) | (1 << (MySQLParser.SPOLY_OVERLAP_POLYGON_NEG - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_POINT - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_POINT_NEG - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_POINT_COM - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_POINT_COM_NEG - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE_NEG - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE_COM - 390)) | (1 << (MySQLParser.SPOLY_CONTAINS_CIRCLE_COM_NEG - 390)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON - 390)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON_NEG - 390)))) != 0) or ((((_la - 454)) & ~0x3f) == 0 and ((1 << (_la - 454)) & ((1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM - 454)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM_NEG - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE_NEG - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE_COM - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_CIRCLE_COM_NEG - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE_NEG - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE_COM - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_LINE_COM_NEG - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE_NEG - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE_COM - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_LINE_COM_NEG - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE_NEG - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM_NEG - 454)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON - 454)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON_NEG - 454)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM - 454)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM_NEG - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE_NEG - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM_NEG - 454)) | (1 << (MySQLParser.STRANS_POLY - 454)) | (1 << (MySQLParser.STRANS_POLY_INVERSE - 454)) | (1 << (MySQLParser.SPOLY_ADD_POINT_AGGR - 454)) | (1 << (MySQLParser.SPOLY_AGGR - 454)) | (1 << (MySQLParser.SPATH - 454)) | (1 << (MySQLParser.SPATH_EQUAL - 454)) | (1 << (MySQLParser.SPATH_EQUAL_NEG - 454)) | (1 << (MySQLParser.SPATH_OVERLAP_PATH - 454)) | (1 << (MySQLParser.SPATH_OVERLAP_PATH_NEG - 454)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT - 454)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT_NEG - 454)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT_COM - 454)) | (1 << (MySQLParser.SPATH_CONTAINS_POINT_COM_NEG - 454)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH - 454)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH_NEG - 454)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH_COM - 454)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_PATH_COM_NEG - 454)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH - 454)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH_NEG - 454)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH_COM - 454)) | (1 << (MySQLParser.SCIRCLE_OVERLAP_PATH_COM_NEG - 454)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE - 454)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE_NEG - 454)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE_COM - 454)) | (1 << (MySQLParser.SPATH_OVERLAP_LINE_COM_NEG - 454)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH - 454)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH_NEG - 454)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH_COM - 454)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_PATH_COM_NEG - 454)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_PATH - 454)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_PATH_NEG - 454)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_PATH_COM - 454)) | (1 << (MySQLParser.SELLIPSE_OVERLAP_PATH_COM_NEG - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH_NEG - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH_COM - 454)) | (1 << (MySQLParser.SPOLY_CONTAINS_PATH_COM_NEG - 454)) | (1 << (MySQLParser.SPOLY_OVERLAP_PATH - 454)))) != 0) or ((((_la - 518)) & ~0x3f) == 0 and ((1 << (_la - 518)) & ((1 << (MySQLParser.SPOLY_OVERLAP_PATH_NEG - 518)) | (1 << (MySQLParser.SPOLY_OVERLAP_PATH_COM - 518)) | (1 << (MySQLParser.SPOLY_OVERLAP_PATH_COM_NEG - 518)) | (1 << (MySQLParser.STRANS_PATH - 518)) | (1 << (MySQLParser.STRANS_PATH_INVERSE - 518)) | (1 << (MySQLParser.SPATH_ADD_POINT_AGGR - 518)) | (1 << (MySQLParser.SPATH_AGGR - 518)) | (1 << (MySQLParser.SBOX - 518)) | (1 << (MySQLParser.SBOX_SW - 518)) | (1 << (MySQLParser.SBOX_SE - 518)) | (1 << (MySQLParser.SBOX_NW - 518)) | (1 << (MySQLParser.SBOX_NE - 518)) | (1 << (MySQLParser.SBOX_EQUAL - 518)) | (1 << (MySQLParser.SBOX_EQUAL_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX_COM - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_BOX_COM_NEG - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_BOX - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_BOX_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT_COM - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_POINT_COM_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE_COM - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_CIRCLE_COM_NEG - 518)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX - 518)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX_NEG - 518)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX_COM - 518)) | (1 << (MySQLParser.SCIRCLE_CONTAINS_BOX_COM_NEG - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE_NEG - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE_COM - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_CIRCLE_COM_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE_COM - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_LINE_COM_NEG - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE_NEG - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE_COM - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_LINE_COM_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE_COM - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_ELLIPSE_COM_NEG - 518)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX - 518)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX_NEG - 518)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX_COM - 518)) | (1 << (MySQLParser.SELLIPSE_CONTAINS_BOX_COM_NEG - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE_NEG - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE_COM - 518)) | (1 << (MySQLParser.SBOX_OVERLAP_ELLIPSE_COM_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_POLY - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_POLY_NEG - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_POLY_COM - 518)) | (1 << (MySQLParser.SBOX_CONTAINS_POLY_COM_NEG - 518)) | (1 << (MySQLParser.SPOLY_CONTAINS_BOX - 518)) | (1 << (MySQLParser.SPOLY_CONTAINS_BOX_NEG - 518)) | (1 << (MySQLParser.SPOLY_CONTAINS_BOX_COM - 518)) | (1 << (MySQLParser.SPOLY_CONTAINS_BOX_COM_NEG - 518)))) != 0) or ((((_la - 582)) & ~0x3f) == 0 and ((1 << (_la - 582)) & ((1 << (MySQLParser.SBOX_OVERLAP_POLY - 582)) | (1 << (MySQLParser.SBOX_OVERLAP_POLY_NEG - 582)) | (1 << (MySQLParser.SBOX_OVERLAP_POLY_COM - 582)) | (1 << (MySQLParser.SBOX_OVERLAP_POLY_COM_NEG - 582)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH - 582)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH_NEG - 582)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH_COM - 582)) | (1 << (MySQLParser.SBOX_CONTAINS_PATH_COM_NEG - 582)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH - 582)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH_NEG - 582)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH_COM - 582)) | (1 << (MySQLParser.SBOX_OVERLAP_PATH_COM_NEG - 582)) | (1 << (MySQLParser.STRRPOS - 582)) | (1 << (MySQLParser.IDLE - 582)) | (1 << (MySQLParser.ANGDIST - 582)) | (1 << (MySQLParser.HILBERTKEY - 582)) | (1 << (MySQLParser.COORDFROMHILBERTKEY - 582)) | (1 << (MySQLParser.SUM_OF_SQUARES - 582)) | (1 << (MySQLParser.PARTITADD_SUM_OF_SQARES - 582)) | (1 << (MySQLParser.GAIA_HEALPIX - 582)) | (1 << (MySQLParser.LPAREN - 582)) | (1 << (MySQLParser.PLUS - 582)) | (1 << (MySQLParser.MINUS - 582)) | (1 << (MySQLParser.NEGATION - 582)) | (1 << (MySQLParser.INTEGER_NUM - 582)) | (1 << (MySQLParser.HEX_DIGIT - 582)) | (1 << (MySQLParser.BIT_NUM - 582)) | (1 << (MySQLParser.REAL_NUMBER - 582)) | (1 << (MySQLParser.TEXT_STRING - 582)) | (1 << (MySQLParser.ID - 582)) | (1 << (MySQLParser.USER_VAR - 582)))) != 0):
                    self.state = 534
                    self.bit_expr()


                self.state = 537
                self.match(MySQLParser.RPAREN)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Groupby_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Groupby_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def GROUP_SYM(self):
            return self.getToken(MySQLParser.GROUP_SYM, 0)

        def BY_SYM(self):
            return self.getToken(MySQLParser.BY_SYM, 0)

        def groupby_item(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Groupby_itemContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Groupby_itemContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.COMMA)
            else:
                return self.getToken(MySQLParser.COMMA, i)

        def WITH(self):
            return self.getToken(MySQLParser.WITH, 0)

        def ROLLUP_SYM(self):
            return self.getToken(MySQLParser.ROLLUP_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_groupby_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterGroupby_clause"):
                listener.enterGroupby_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitGroupby_clause"):
                listener.exitGroupby_clause(self)




    def groupby_clause(self):

        localctx = MySQLParser.Groupby_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 84, self.RULE_groupby_clause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 541
            self.match(MySQLParser.GROUP_SYM)
            self.state = 542
            self.match(MySQLParser.BY_SYM)
            self.state = 543
            self.groupby_item()
            self.state = 548
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MySQLParser.COMMA:
                self.state = 544
                self.match(MySQLParser.COMMA)
                self.state = 545
                self.groupby_item()
                self.state = 550
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 553
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.WITH:
                self.state = 551
                self.match(MySQLParser.WITH)
                self.state = 552
                self.match(MySQLParser.ROLLUP_SYM)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Groupby_itemContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Groupby_itemContext, self).__init__(parent, invokingState)
            self.parser = parser

        def column_spec(self):
            return self.getTypedRuleContext(MySQLParser.Column_specContext,0)


        def INTEGER_NUM(self):
            return self.getToken(MySQLParser.INTEGER_NUM, 0)

        def bit_expr(self):
            return self.getTypedRuleContext(MySQLParser.Bit_exprContext,0)


        def ASC(self):
            return self.getToken(MySQLParser.ASC, 0)

        def DESC(self):
            return self.getToken(MySQLParser.DESC, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_groupby_item

        def enterRule(self, listener):
            if hasattr(listener, "enterGroupby_item"):
                listener.enterGroupby_item(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitGroupby_item"):
                listener.exitGroupby_item(self)




    def groupby_item(self):

        localctx = MySQLParser.Groupby_itemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 86, self.RULE_groupby_item)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 558
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,65,self._ctx)
            if la_ == 1:
                self.state = 555
                self.column_spec()
                pass

            elif la_ == 2:
                self.state = 556
                self.match(MySQLParser.INTEGER_NUM)
                pass

            elif la_ == 3:
                self.state = 557
                self.bit_expr()
                pass


            self.state = 561
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,66,self._ctx)
            if la_ == 1:
                self.state = 560
                _la = self._input.LA(1)
                if not(_la==MySQLParser.ASC or _la==MySQLParser.DESC):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Having_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Having_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def HAVING(self):
            return self.getToken(MySQLParser.HAVING, 0)

        def expression(self):
            return self.getTypedRuleContext(MySQLParser.ExpressionContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_having_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterHaving_clause"):
                listener.enterHaving_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitHaving_clause"):
                listener.exitHaving_clause(self)




    def having_clause(self):

        localctx = MySQLParser.Having_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 88, self.RULE_having_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 563
            self.match(MySQLParser.HAVING)
            self.state = 564
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Index_hintContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Index_hintContext, self).__init__(parent, invokingState)
            self.parser = parser

        def USE_SYM(self):
            return self.getToken(MySQLParser.USE_SYM, 0)

        def index_options(self):
            return self.getTypedRuleContext(MySQLParser.Index_optionsContext,0)


        def LPAREN(self):
            return self.getToken(MySQLParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(MySQLParser.RPAREN, 0)

        def index_list(self):
            return self.getTypedRuleContext(MySQLParser.Index_listContext,0)


        def IGNORE_SYM(self):
            return self.getToken(MySQLParser.IGNORE_SYM, 0)

        def FORCE_SYM(self):
            return self.getToken(MySQLParser.FORCE_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_index_hint

        def enterRule(self, listener):
            if hasattr(listener, "enterIndex_hint"):
                listener.enterIndex_hint(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitIndex_hint"):
                listener.exitIndex_hint(self)




    def index_hint(self):

        localctx = MySQLParser.Index_hintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 90, self.RULE_index_hint)
        self._la = 0 # Token type
        try:
            self.state = 586
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [MySQLParser.USE_SYM]:
                self.enterOuterAlt(localctx, 1)
                self.state = 566
                self.match(MySQLParser.USE_SYM)
                self.state = 567
                self.index_options()
                self.state = 568
                self.match(MySQLParser.LPAREN)
                self.state = 570
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.ID:
                    self.state = 569
                    self.index_list()


                self.state = 572
                self.match(MySQLParser.RPAREN)
                pass
            elif token in [MySQLParser.IGNORE_SYM]:
                self.enterOuterAlt(localctx, 2)
                self.state = 574
                self.match(MySQLParser.IGNORE_SYM)
                self.state = 575
                self.index_options()
                self.state = 576
                self.match(MySQLParser.LPAREN)
                self.state = 577
                self.index_list()
                self.state = 578
                self.match(MySQLParser.RPAREN)
                pass
            elif token in [MySQLParser.FORCE_SYM]:
                self.enterOuterAlt(localctx, 3)
                self.state = 580
                self.match(MySQLParser.FORCE_SYM)
                self.state = 581
                self.index_options()
                self.state = 582
                self.match(MySQLParser.LPAREN)
                self.state = 583
                self.index_list()
                self.state = 584
                self.match(MySQLParser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Index_hint_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Index_hint_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def index_hint(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Index_hintContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Index_hintContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.COMMA)
            else:
                return self.getToken(MySQLParser.COMMA, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_index_hint_list

        def enterRule(self, listener):
            if hasattr(listener, "enterIndex_hint_list"):
                listener.enterIndex_hint_list(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitIndex_hint_list"):
                listener.exitIndex_hint_list(self)




    def index_hint_list(self):

        localctx = MySQLParser.Index_hint_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 92, self.RULE_index_hint_list)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 588
            self.index_hint()
            self.state = 593
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,69,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 589
                    self.match(MySQLParser.COMMA)
                    self.state = 590
                    self.index_hint() 
                self.state = 595
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,69,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Index_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Index_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(MySQLParser.ID, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_index_name

        def enterRule(self, listener):
            if hasattr(listener, "enterIndex_name"):
                listener.enterIndex_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitIndex_name"):
                listener.exitIndex_name(self)




    def index_name(self):

        localctx = MySQLParser.Index_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 94, self.RULE_index_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 596
            self.match(MySQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Index_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Index_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def index_name(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Index_nameContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Index_nameContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.COMMA)
            else:
                return self.getToken(MySQLParser.COMMA, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_index_list

        def enterRule(self, listener):
            if hasattr(listener, "enterIndex_list"):
                listener.enterIndex_list(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitIndex_list"):
                listener.exitIndex_list(self)




    def index_list(self):

        localctx = MySQLParser.Index_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 96, self.RULE_index_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 598
            self.index_name()
            self.state = 603
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MySQLParser.COMMA:
                self.state = 599
                self.match(MySQLParser.COMMA)
                self.state = 600
                self.index_name()
                self.state = 605
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Index_optionsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Index_optionsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def INDEX_SYM(self):
            return self.getToken(MySQLParser.INDEX_SYM, 0)

        def KEY_SYM(self):
            return self.getToken(MySQLParser.KEY_SYM, 0)

        def FOR_SYM(self):
            return self.getToken(MySQLParser.FOR_SYM, 0)

        def JOIN_SYM(self):
            return self.getToken(MySQLParser.JOIN_SYM, 0)

        def ORDER_SYM(self):
            return self.getToken(MySQLParser.ORDER_SYM, 0)

        def BY_SYM(self):
            return self.getToken(MySQLParser.BY_SYM, 0)

        def GROUP_SYM(self):
            return self.getToken(MySQLParser.GROUP_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_index_options

        def enterRule(self, listener):
            if hasattr(listener, "enterIndex_options"):
                listener.enterIndex_options(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitIndex_options"):
                listener.exitIndex_options(self)




    def index_options(self):

        localctx = MySQLParser.Index_optionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 98, self.RULE_index_options)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 606
            _la = self._input.LA(1)
            if not(_la==MySQLParser.INDEX_SYM or _la==MySQLParser.KEY_SYM):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 615
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.FOR_SYM:
                self.state = 607
                self.match(MySQLParser.FOR_SYM)
                self.state = 613
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [MySQLParser.JOIN_SYM]:
                    self.state = 608
                    self.match(MySQLParser.JOIN_SYM)
                    pass
                elif token in [MySQLParser.ORDER_SYM]:
                    self.state = 609
                    self.match(MySQLParser.ORDER_SYM)
                    self.state = 610
                    self.match(MySQLParser.BY_SYM)
                    pass
                elif token in [MySQLParser.GROUP_SYM]:
                    self.state = 611
                    self.match(MySQLParser.GROUP_SYM)
                    self.state = 612
                    self.match(MySQLParser.BY_SYM)
                    pass
                else:
                    raise NoViableAltException(self)



        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Interval_exprContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Interval_exprContext, self).__init__(parent, invokingState)
            self.parser = parser

        def INTERVAL_SYM(self):
            return self.getToken(MySQLParser.INTERVAL_SYM, 0)

        def expression(self):
            return self.getTypedRuleContext(MySQLParser.ExpressionContext,0)


        def interval_unit(self):
            return self.getTypedRuleContext(MySQLParser.Interval_unitContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_interval_expr

        def enterRule(self, listener):
            if hasattr(listener, "enterInterval_expr"):
                listener.enterInterval_expr(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitInterval_expr"):
                listener.exitInterval_expr(self)




    def interval_expr(self):

        localctx = MySQLParser.Interval_exprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 100, self.RULE_interval_expr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 617
            self.match(MySQLParser.INTERVAL_SYM)
            self.state = 618
            self.expression()
            self.state = 619
            self.interval_unit()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Join_conditionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Join_conditionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ON(self):
            return self.getToken(MySQLParser.ON, 0)

        def expression(self):
            return self.getTypedRuleContext(MySQLParser.ExpressionContext,0)


        def USING_SYM(self):
            return self.getToken(MySQLParser.USING_SYM, 0)

        def column_list(self):
            return self.getTypedRuleContext(MySQLParser.Column_listContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_join_condition

        def enterRule(self, listener):
            if hasattr(listener, "enterJoin_condition"):
                listener.enterJoin_condition(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitJoin_condition"):
                listener.exitJoin_condition(self)




    def join_condition(self):

        localctx = MySQLParser.Join_conditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 102, self.RULE_join_condition)
        try:
            self.state = 625
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [MySQLParser.ON]:
                self.enterOuterAlt(localctx, 1)
                self.state = 621
                self.match(MySQLParser.ON)
                self.state = 622
                self.expression()
                pass
            elif token in [MySQLParser.USING_SYM]:
                self.enterOuterAlt(localctx, 2)
                self.state = 623
                self.match(MySQLParser.USING_SYM)
                self.state = 624
                self.column_list()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Limit_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Limit_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LIMIT(self):
            return self.getToken(MySQLParser.LIMIT, 0)

        def row_count(self):
            return self.getTypedRuleContext(MySQLParser.Row_countContext,0)


        def offset(self):
            return self.getTypedRuleContext(MySQLParser.OffsetContext,0)


        def COMMA(self):
            return self.getToken(MySQLParser.COMMA, 0)

        def OFFSET_SYM(self):
            return self.getToken(MySQLParser.OFFSET_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_limit_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterLimit_clause"):
                listener.enterLimit_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitLimit_clause"):
                listener.exitLimit_clause(self)




    def limit_clause(self):

        localctx = MySQLParser.Limit_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 104, self.RULE_limit_clause)
        try:
            self.state = 638
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [MySQLParser.LIMIT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 627
                self.match(MySQLParser.LIMIT)

                self.state = 631
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,74,self._ctx)
                if la_ == 1:
                    self.state = 628
                    self.offset()
                    self.state = 629
                    self.match(MySQLParser.COMMA)


                self.state = 633
                self.row_count()
                pass
            elif token in [MySQLParser.INTEGER_NUM]:
                self.enterOuterAlt(localctx, 2)
                self.state = 634
                self.row_count()
                self.state = 635
                self.match(MySQLParser.OFFSET_SYM)
                self.state = 636
                self.offset()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Match_against_statementContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Match_against_statementContext, self).__init__(parent, invokingState)
            self.parser = parser

        def MATCH(self):
            return self.getToken(MySQLParser.MATCH, 0)

        def AGAINST(self):
            return self.getToken(MySQLParser.AGAINST, 0)

        def column_spec(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Column_specContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Column_specContext,i)


        def expression(self):
            return self.getTypedRuleContext(MySQLParser.ExpressionContext,0)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.COMMA)
            else:
                return self.getToken(MySQLParser.COMMA, i)

        def search_modifier(self):
            return self.getTypedRuleContext(MySQLParser.Search_modifierContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_match_against_statement

        def enterRule(self, listener):
            if hasattr(listener, "enterMatch_against_statement"):
                listener.enterMatch_against_statement(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMatch_against_statement"):
                listener.exitMatch_against_statement(self)




    def match_against_statement(self):

        localctx = MySQLParser.Match_against_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 106, self.RULE_match_against_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 640
            self.match(MySQLParser.MATCH)

            self.state = 641
            self.column_spec()
            self.state = 646
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MySQLParser.COMMA:
                self.state = 642
                self.match(MySQLParser.COMMA)
                self.state = 643
                self.column_spec()
                self.state = 648
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 649
            self.match(MySQLParser.AGAINST)

            self.state = 650
            self.expression()
            self.state = 652
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,77,self._ctx)
            if la_ == 1:
                self.state = 651
                self.search_modifier()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class OffsetContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.OffsetContext, self).__init__(parent, invokingState)
            self.parser = parser

        def INTEGER_NUM(self):
            return self.getToken(MySQLParser.INTEGER_NUM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_offset

        def enterRule(self, listener):
            if hasattr(listener, "enterOffset"):
                listener.enterOffset(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOffset"):
                listener.exitOffset(self)




    def offset(self):

        localctx = MySQLParser.OffsetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 108, self.RULE_offset)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 654
            self.match(MySQLParser.INTEGER_NUM)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Row_countContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Row_countContext, self).__init__(parent, invokingState)
            self.parser = parser

        def INTEGER_NUM(self):
            return self.getToken(MySQLParser.INTEGER_NUM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_row_count

        def enterRule(self, listener):
            if hasattr(listener, "enterRow_count"):
                listener.enterRow_count(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitRow_count"):
                listener.exitRow_count(self)




    def row_count(self):

        localctx = MySQLParser.Row_countContext(self, self._ctx, self.state)
        self.enterRule(localctx, 110, self.RULE_row_count)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 656
            self.match(MySQLParser.INTEGER_NUM)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Orderby_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Orderby_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ORDER_SYM(self):
            return self.getToken(MySQLParser.ORDER_SYM, 0)

        def BY_SYM(self):
            return self.getToken(MySQLParser.BY_SYM, 0)

        def orderby_item(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Orderby_itemContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Orderby_itemContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.COMMA)
            else:
                return self.getToken(MySQLParser.COMMA, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_orderby_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterOrderby_clause"):
                listener.enterOrderby_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOrderby_clause"):
                listener.exitOrderby_clause(self)




    def orderby_clause(self):

        localctx = MySQLParser.Orderby_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 112, self.RULE_orderby_clause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 658
            self.match(MySQLParser.ORDER_SYM)
            self.state = 659
            self.match(MySQLParser.BY_SYM)
            self.state = 660
            self.orderby_item()
            self.state = 665
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MySQLParser.COMMA:
                self.state = 661
                self.match(MySQLParser.COMMA)
                self.state = 662
                self.orderby_item()
                self.state = 667
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Orderby_itemContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Orderby_itemContext, self).__init__(parent, invokingState)
            self.parser = parser

        def groupby_item(self):
            return self.getTypedRuleContext(MySQLParser.Groupby_itemContext,0)


        def ASC(self):
            return self.getToken(MySQLParser.ASC, 0)

        def DESC(self):
            return self.getToken(MySQLParser.DESC, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_orderby_item

        def enterRule(self, listener):
            if hasattr(listener, "enterOrderby_item"):
                listener.enterOrderby_item(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOrderby_item"):
                listener.exitOrderby_item(self)




    def orderby_item(self):

        localctx = MySQLParser.Orderby_itemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 114, self.RULE_orderby_item)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 668
            self.groupby_item()
            self.state = 670
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.ASC or _la==MySQLParser.DESC:
                self.state = 669
                _la = self._input.LA(1)
                if not(_la==MySQLParser.ASC or _la==MySQLParser.DESC):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Partition_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Partition_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def PARTITION_SYM(self):
            return self.getToken(MySQLParser.PARTITION_SYM, 0)

        def LPAREN(self):
            return self.getToken(MySQLParser.LPAREN, 0)

        def partition_names(self):
            return self.getTypedRuleContext(MySQLParser.Partition_namesContext,0)


        def RPAREN(self):
            return self.getToken(MySQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_partition_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterPartition_clause"):
                listener.enterPartition_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPartition_clause"):
                listener.exitPartition_clause(self)




    def partition_clause(self):

        localctx = MySQLParser.Partition_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 116, self.RULE_partition_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 672
            self.match(MySQLParser.PARTITION_SYM)
            self.state = 673
            self.match(MySQLParser.LPAREN)
            self.state = 674
            self.partition_names()
            self.state = 675
            self.match(MySQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Partition_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Partition_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(MySQLParser.ID, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_partition_name

        def enterRule(self, listener):
            if hasattr(listener, "enterPartition_name"):
                listener.enterPartition_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPartition_name"):
                listener.exitPartition_name(self)




    def partition_name(self):

        localctx = MySQLParser.Partition_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 118, self.RULE_partition_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 677
            self.match(MySQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Partition_namesContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Partition_namesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def partition_name(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Partition_nameContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Partition_nameContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.COMMA)
            else:
                return self.getToken(MySQLParser.COMMA, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_partition_names

        def enterRule(self, listener):
            if hasattr(listener, "enterPartition_names"):
                listener.enterPartition_names(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPartition_names"):
                listener.exitPartition_names(self)




    def partition_names(self):

        localctx = MySQLParser.Partition_namesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 120, self.RULE_partition_names)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 679
            self.partition_name()
            self.state = 684
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MySQLParser.COMMA:
                self.state = 680
                self.match(MySQLParser.COMMA)
                self.state = 681
                self.partition_name()
                self.state = 686
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Bit_fac1Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Bit_fac1Context, self).__init__(parent, invokingState)
            self.parser = parser

        def NOT_SYM(self):
            return self.getToken(MySQLParser.NOT_SYM, 0)

        def IN_SYM(self):
            return self.getToken(MySQLParser.IN_SYM, 0)

        def LIKE_SYM(self):
            return self.getToken(MySQLParser.LIKE_SYM, 0)

        def simple_expr(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Simple_exprContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Simple_exprContext,i)


        def REGEXP(self):
            return self.getToken(MySQLParser.REGEXP, 0)

        def bit_expr(self):
            return self.getTypedRuleContext(MySQLParser.Bit_exprContext,0)


        def BETWEEN(self):
            return self.getToken(MySQLParser.BETWEEN, 0)

        def AND_SYM(self):
            return self.getToken(MySQLParser.AND_SYM, 0)

        def predicate(self):
            return self.getTypedRuleContext(MySQLParser.PredicateContext,0)


        def subquery(self):
            return self.getTypedRuleContext(MySQLParser.SubqueryContext,0)


        def expression_list(self):
            return self.getTypedRuleContext(MySQLParser.Expression_listContext,0)


        def ESCAPE_SYM(self):
            return self.getToken(MySQLParser.ESCAPE_SYM, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_bit_fac1

        def enterRule(self, listener):
            if hasattr(listener, "enterBit_fac1"):
                listener.enterBit_fac1(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBit_fac1"):
                listener.exitBit_fac1(self)




    def bit_fac1(self):

        localctx = MySQLParser.Bit_fac1Context(self, self._ctx, self.state)
        self.enterRule(localctx, 122, self.RULE_bit_fac1)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 688
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.NOT_SYM:
                self.state = 687
                self.match(MySQLParser.NOT_SYM)


            self.state = 708
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [MySQLParser.IN_SYM]:
                self.state = 690
                self.match(MySQLParser.IN_SYM)
                self.state = 693
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,82,self._ctx)
                if la_ == 1:
                    self.state = 691
                    self.subquery()
                    pass

                elif la_ == 2:
                    self.state = 692
                    self.expression_list()
                    pass


                pass
            elif token in [MySQLParser.LIKE_SYM]:
                self.state = 695
                self.match(MySQLParser.LIKE_SYM)
                self.state = 696
                self.simple_expr()
                self.state = 699
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,83,self._ctx)
                if la_ == 1:
                    self.state = 697
                    self.match(MySQLParser.ESCAPE_SYM)
                    self.state = 698
                    self.simple_expr()


                pass
            elif token in [MySQLParser.REGEXP]:
                self.state = 701
                self.match(MySQLParser.REGEXP)
                self.state = 702
                self.bit_expr()
                pass
            elif token in [MySQLParser.BETWEEN]:
                self.state = 703
                self.match(MySQLParser.BETWEEN)
                self.state = 704
                self.bit_expr()
                self.state = 705
                self.match(MySQLParser.AND_SYM)
                self.state = 706
                self.predicate()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Bit_fac2Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Bit_fac2Context, self).__init__(parent, invokingState)
            self.parser = parser

        def SOUNDS_SYM(self):
            return self.getToken(MySQLParser.SOUNDS_SYM, 0)

        def LIKE_SYM(self):
            return self.getToken(MySQLParser.LIKE_SYM, 0)

        def bit_expr(self):
            return self.getTypedRuleContext(MySQLParser.Bit_exprContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_bit_fac2

        def enterRule(self, listener):
            if hasattr(listener, "enterBit_fac2"):
                listener.enterBit_fac2(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBit_fac2"):
                listener.exitBit_fac2(self)




    def bit_fac2(self):

        localctx = MySQLParser.Bit_fac2Context(self, self._ctx, self.state)
        self.enterRule(localctx, 124, self.RULE_bit_fac2)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 710
            self.match(MySQLParser.SOUNDS_SYM)
            self.state = 711
            self.match(MySQLParser.LIKE_SYM)
            self.state = 712
            self.bit_expr()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PredicateContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.PredicateContext, self).__init__(parent, invokingState)
            self.parser = parser

        def bit_expr(self):
            return self.getTypedRuleContext(MySQLParser.Bit_exprContext,0)


        def bit_fac1(self):
            return self.getTypedRuleContext(MySQLParser.Bit_fac1Context,0)


        def bit_fac2(self):
            return self.getTypedRuleContext(MySQLParser.Bit_fac2Context,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_predicate

        def enterRule(self, listener):
            if hasattr(listener, "enterPredicate"):
                listener.enterPredicate(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPredicate"):
                listener.exitPredicate(self)




    def predicate(self):

        localctx = MySQLParser.PredicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 126, self.RULE_predicate)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 714
            self.bit_expr()

            self.state = 717
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,85,self._ctx)
            if la_ == 1:
                self.state = 715
                self.bit_fac1()

            elif la_ == 2:
                self.state = 716
                self.bit_fac2()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class QueryContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.QueryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def select_statement(self):
            return self.getTypedRuleContext(MySQLParser.Select_statementContext,0)


        def SEMI(self):
            return self.getToken(MySQLParser.SEMI, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_query

        def enterRule(self, listener):
            if hasattr(listener, "enterQuery"):
                listener.enterQuery(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitQuery"):
                listener.exitQuery(self)




    def query(self):

        localctx = MySQLParser.QueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 128, self.RULE_query)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 719
            self.select_statement()
            self.state = 720
            self.match(MySQLParser.SEMI)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Schema_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Schema_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(MySQLParser.ID, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_schema_name

        def enterRule(self, listener):
            if hasattr(listener, "enterSchema_name"):
                listener.enterSchema_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSchema_name"):
                listener.exitSchema_name(self)




    def schema_name(self):

        localctx = MySQLParser.Schema_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 130, self.RULE_schema_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 722
            self.match(MySQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Select_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Select_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def displayed_column(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Displayed_columnContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Displayed_columnContext,i)


        def ASTERISK(self):
            return self.getToken(MySQLParser.ASTERISK, 0)

        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.COMMA)
            else:
                return self.getToken(MySQLParser.COMMA, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_select_list

        def enterRule(self, listener):
            if hasattr(listener, "enterSelect_list"):
                listener.enterSelect_list(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSelect_list"):
                listener.exitSelect_list(self)




    def select_list(self):

        localctx = MySQLParser.Select_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 132, self.RULE_select_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 744
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [MySQLParser.ABS, MySQLParser.ACOS, MySQLParser.ADDDATE, MySQLParser.ADDTIME, MySQLParser.AES_DECRYPT, MySQLParser.AES_ENCRYPT, MySQLParser.ASCII_SYM, MySQLParser.ASIN, MySQLParser.ATAN, MySQLParser.ATAN2, MySQLParser.AVG, MySQLParser.BENCHMARK, MySQLParser.BIN, MySQLParser.BINARY, MySQLParser.BIT_AND, MySQLParser.BIT_COUNT, MySQLParser.BIT_LENGTH, MySQLParser.BIT_OR, MySQLParser.BIT_XOR, MySQLParser.CASE_SYM, MySQLParser.CAST_SYM, MySQLParser.CEIL, MySQLParser.CEILING, MySQLParser.CHAR, MySQLParser.CHARSET, MySQLParser.CHAR_LENGTH, MySQLParser.COERCIBILITY, MySQLParser.COLLATION, MySQLParser.CONCAT, MySQLParser.CONCAT_WS, MySQLParser.CONNECTION_ID, MySQLParser.CONV, MySQLParser.CONVERT_SYM, MySQLParser.CONVERT_TZ, MySQLParser.COS, MySQLParser.COT, MySQLParser.COUNT, MySQLParser.CRC32, MySQLParser.CURDATE, MySQLParser.CURRENT_USER, MySQLParser.CURTIME, MySQLParser.DATABASE, MySQLParser.DATEDIFF, MySQLParser.DATE_ADD, MySQLParser.DATE_FORMAT, MySQLParser.DATE_SUB, MySQLParser.DATE_SYM, MySQLParser.DAYNAME, MySQLParser.DAYOFMONTH, MySQLParser.DAYOFWEEK, MySQLParser.DAYOFYEAR, MySQLParser.DECODE, MySQLParser.DEFAULT, MySQLParser.DEGREES, MySQLParser.DES_DECRYPT, MySQLParser.DES_ENCRYPT, MySQLParser.ELT, MySQLParser.ENCODE, MySQLParser.ENCRYPT, MySQLParser.EXISTS, MySQLParser.EXP, MySQLParser.EXPORT_SET, MySQLParser.EXTRACT, MySQLParser.FALSE_SYM, MySQLParser.FIELD, MySQLParser.FIND_IN_SET, MySQLParser.FLOOR, MySQLParser.FORMAT, MySQLParser.FOUND_ROWS, MySQLParser.FROM_BASE64, MySQLParser.FROM_DAYS, MySQLParser.FROM_UNIXTIME, MySQLParser.GET_FORMAT, MySQLParser.GET_LOCK, MySQLParser.GROUP_CONCAT, MySQLParser.HEX, MySQLParser.HOUR, MySQLParser.IF, MySQLParser.IFNULL, MySQLParser.INET_ATON, MySQLParser.INET_NTOA, MySQLParser.INSERT, MySQLParser.INSTR, MySQLParser.INTERVAL_SYM, MySQLParser.IS_FREE_LOCK, MySQLParser.IS_USED_LOCK, MySQLParser.LAST_DAY, MySQLParser.LAST_INSERT_ID, MySQLParser.LEFT, MySQLParser.LENGTH, MySQLParser.LN, MySQLParser.LOAD_FILE, MySQLParser.LOCATE, MySQLParser.LOG, MySQLParser.LOG10, MySQLParser.LOG2, MySQLParser.LOWER, MySQLParser.LPAD, MySQLParser.LTRIM, MySQLParser.MAKEDATE, MySQLParser.MAKETIME, MySQLParser.MAKE_SET, MySQLParser.MASTER_POS_WAIT, MySQLParser.MATCH, MySQLParser.MAX_SYM, MySQLParser.MD5, MySQLParser.MICROSECOND, MySQLParser.MID, MySQLParser.MINUTE, MySQLParser.MIN_SYM, MySQLParser.MOD, MySQLParser.MONTH, MySQLParser.MONTHNAME, MySQLParser.NAME_CONST, MySQLParser.NOW, MySQLParser.NULL_SYM, MySQLParser.OCT, MySQLParser.OLD_PASSWORD, MySQLParser.ORD, MySQLParser.PASSWORD, MySQLParser.PERIOD_ADD, MySQLParser.PERIOD_DIFF, MySQLParser.PI, MySQLParser.POW, MySQLParser.POWER, MySQLParser.QUARTER, MySQLParser.QUOTE, MySQLParser.RADIANS, MySQLParser.RAND, MySQLParser.RELEASE_LOCK, MySQLParser.REPEAT, MySQLParser.REPLACE, MySQLParser.REVERSE, MySQLParser.RIGHT, MySQLParser.ROUND, MySQLParser.ROW_SYM, MySQLParser.RPAD, MySQLParser.RTRIM, MySQLParser.SCHEMA, MySQLParser.SECOND, MySQLParser.SEC_TO_TIME, MySQLParser.SESSION_USER, MySQLParser.SIGN, MySQLParser.SIN, MySQLParser.SLEEP, MySQLParser.SOUNDEX, MySQLParser.SPACE, MySQLParser.SQRT, MySQLParser.STD, MySQLParser.STDDEV, MySQLParser.STDDEV_POP, MySQLParser.STDDEV_SAMP, MySQLParser.STRCMP, MySQLParser.STR_TO_DATE, MySQLParser.SUBSTRING, MySQLParser.SUBSTRING_INDEX, MySQLParser.SUBTIME, MySQLParser.SUM, MySQLParser.SYSDATE, MySQLParser.SYSTEM_USER, MySQLParser.TAN, MySQLParser.TIMEDIFF, MySQLParser.TIMESTAMP, MySQLParser.TIMESTAMPADD, MySQLParser.TIMESTAMPDIFF, MySQLParser.TIME_FORMAT, MySQLParser.TIME_SYM, MySQLParser.TIME_TO_SEC, MySQLParser.TO_BASE64, MySQLParser.TO_DAYS, MySQLParser.TO_SECONDS, MySQLParser.TRIM, MySQLParser.TRUE_SYM, MySQLParser.TRUNCATE, MySQLParser.UNHEX, MySQLParser.UNIX_TIMESTAMP, MySQLParser.UPPER, MySQLParser.USER, MySQLParser.UTC_DATE, MySQLParser.UTC_TIME, MySQLParser.UTC_TIMESTAMP, MySQLParser.UUID, MySQLParser.VALUES, MySQLParser.VARIANCE, MySQLParser.VAR_POP, MySQLParser.VAR_SAMP, MySQLParser.VERSION_SYM, MySQLParser.WEEK, MySQLParser.WEEKDAY, MySQLParser.WEEKOFYEAR, MySQLParser.WEIGHT_STRING, MySQLParser.YEAR, MySQLParser.YEARWEEK, MySQLParser.SDIST, MySQLParser.SAREA, MySQLParser.SCENTER, MySQLParser.SCIRCUM, MySQLParser.SLENGTH, MySQLParser.SSWAP, MySQLParser.SNPOINTS, MySQLParser.SSTR, MySQLParser.MYSQL_SPHERE_VERSION, MySQLParser.SRCONTAINSL, MySQLParser.SLCONTAINSR, MySQLParser.SRNOTCONTAINSL, MySQLParser.SLNOTCONTAINSR, MySQLParser.SOVERLAPS, MySQLParser.SNOTOVERLAPS, MySQLParser.SEQUAL, MySQLParser.SNOTEQUAL, MySQLParser.STRANSFORM, MySQLParser.SINVERSE, MySQLParser.SPOINT, MySQLParser.SPOINT_LONG, MySQLParser.SPOINT_LAT, MySQLParser.SPOINT_X, MySQLParser.SPOINT_Y, MySQLParser.SPOINT_Z, MySQLParser.SPOINT_EQUAL, MySQLParser.STRANS, MySQLParser.STRANS_POINT, MySQLParser.STRANS_POINT_INVERSE, MySQLParser.STRANS_EQUAL, MySQLParser.STRANS_EQUAL_NEG, MySQLParser.STRANS_PHI, MySQLParser.STRANS_THETA, MySQLParser.STRANS_PSI, MySQLParser.STRANS_AXES, MySQLParser.STRANS_INVERT, MySQLParser.STRANS_ZXZ, MySQLParser.STRANS_TRANS, MySQLParser.STRANS_TRANS_INV, MySQLParser.SCIRCLE, MySQLParser.SCIRCLE_RADIUS, MySQLParser.SCIRCLE_EQUAL, MySQLParser.SCIRCLE_EQUAL_NEG, MySQLParser.SCIRCLE_OVERLAP, MySQLParser.SCIRCLE_OVERLAP_NEG, MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE, MySQLParser.SCIRCLE_CONTAINED_BY_CIRCLE_NEG, MySQLParser.SCIRCLE_CONTAINS_CIRCLE, MySQLParser.SCIRCLE_CONTAINS_CIRCLE_NEG, MySQLParser.SPOINT_CONTAINED_BY_CIRCLE, MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_NEG, MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM, MySQLParser.SPOINT_CONTAINED_BY_CIRCLE_COM_NEG, MySQLParser.STRANS_CIRCLE, MySQLParser.STRANS_CIRCLE_INVERSE, MySQLParser.SLINE, MySQLParser.SMERIDIAN, MySQLParser.SLINE_BEG, MySQLParser.SLINE_END, MySQLParser.SLINE_EQUAL, MySQLParser.SLINE_EQUAL_NEG, MySQLParser.SLINE_TURN, MySQLParser.SLINE_CROSSES, MySQLParser.SLINE_CROSSES_NEG, MySQLParser.SLINE_OVERLAP, MySQLParser.SLINE_CONTAINS_POINT, MySQLParser.SLINE_CONTAINS_POINT_COM, MySQLParser.SLINE_CONTAINS_POINT_NEG, MySQLParser.SLINE_CONTAINS_POINT_COM_NEG, MySQLParser.STRANS_LINE, MySQLParser.STRANS_LINE_INVERSE, MySQLParser.SLINE_OVERLAP_CIRCLE, MySQLParser.SLINE_OVERLAP_CIRCLE_COM, MySQLParser.SLINE_OVERLAP_CIRCLE_NEG, MySQLParser.SLINE_OVERLAP_CIRCLE_COM_NEG, MySQLParser.SCIRCLE_CONTAINS_LINE, MySQLParser.SCIRCLE_CONTAINS_LINE_COM, MySQLParser.SCIRCLE_CONTAINS_LINE_NEG, MySQLParser.SCIRCLE_CONTAINS_LINE_COM_NEG, MySQLParser.SELLIPSE, MySQLParser.SELLIPSE_INC, MySQLParser.SELLIPSE_LRAD, MySQLParser.SELLIPSE_SRAD, MySQLParser.SELLIPSE_EQUAL, MySQLParser.SELLIPSE_EQUAL_NEG, MySQLParser.SELLIPSE_CONTAINS_ELLIPSE, MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_NEG, MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM, MySQLParser.SELLIPSE_CONTAINS_ELLIPSE_COM_NEG, MySQLParser.SELLIPSE_OVERLAP_ELLIPSE, MySQLParser.SELLIPSE_OVERLAP_ELLIPSE_NEG, MySQLParser.SELLIPSE_CONTAINS_POINT, MySQLParser.SELLIPSE_CONTAINS_POINT_NEG, MySQLParser.SELLIPSE_CONTAINS_POINT_COM, MySQLParser.SELLIPSE_CONTAINS_POINT_COM_NEG, MySQLParser.SELLIPSE_CONTAINS_CIRCLE, MySQLParser.SELLIPSE_CONTAINS_CIRCLE_NEG, MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM, MySQLParser.SELLIPSE_CONTAINS_CIRCLE_COM_NEG, MySQLParser.SCIRCLE_CONTAINS_ELLIPSE, MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_NEG, MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM, MySQLParser.SCIRCLE_CONTAINS_ELLIPSE_COM_NEG, MySQLParser.SELLIPSE_OVERLAP_CIRCLE, MySQLParser.SELLIPSE_OVERLAP_CIRCLE_NEG, MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM, MySQLParser.SELLIPSE_OVERLAP_CIRCLE_COM_NEG, MySQLParser.SELLIPSE_OVERLAP_LINE, MySQLParser.SELLIPSE_OVERLAP_LINE_NEG, MySQLParser.SELLIPSE_OVERLAP_LINE_COM, MySQLParser.SELLIPSE_OVERLAP_LINE_COM_NEG, MySQLParser.SELLIPSE_CONTAINS_LINE, MySQLParser.SELLIPSE_CONTAINS_LINE_NEG, MySQLParser.SELLIPSE_CONTAINS_LINE_COM, MySQLParser.SELLIPSE_CONTAINS_LINE_COM_NEG, MySQLParser.STRANS_ELLIPSE, MySQLParser.STRANS_ELLIPSE_INVERSE, MySQLParser.SPOLY, MySQLParser.SPOLY_EQUAL, MySQLParser.SPOLY_EQUAL_NEG, MySQLParser.SPOLY_CONTAINS_POLYGON, MySQLParser.SPOLY_CONTAINS_POLYGON_NEG, MySQLParser.SPOLY_CONTAINS_POLYGON_COM, MySQLParser.SPOLY_CONTAINS_POLYGON_COM_NEG, MySQLParser.SPOLY_OVERLAP_POLYGON, MySQLParser.SPOLY_OVERLAP_POLYGON_NEG, MySQLParser.SPOLY_CONTAINS_POINT, MySQLParser.SPOLY_CONTAINS_POINT_NEG, MySQLParser.SPOLY_CONTAINS_POINT_COM, MySQLParser.SPOLY_CONTAINS_POINT_COM_NEG, MySQLParser.SPOLY_CONTAINS_CIRCLE, MySQLParser.SPOLY_CONTAINS_CIRCLE_NEG, MySQLParser.SPOLY_CONTAINS_CIRCLE_COM, MySQLParser.SPOLY_CONTAINS_CIRCLE_COM_NEG, MySQLParser.SCIRCLE_CONTAINS_POLYGON, MySQLParser.SCIRCLE_CONTAINS_POLYGON_NEG, MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM, MySQLParser.SCIRCLE_CONTAINS_POLYGON_COM_NEG, MySQLParser.SPOLY_OVERLAP_CIRCLE, MySQLParser.SPOLY_OVERLAP_CIRCLE_NEG, MySQLParser.SPOLY_OVERLAP_CIRCLE_COM, MySQLParser.SPOLY_OVERLAP_CIRCLE_COM_NEG, MySQLParser.SPOLY_CONTAINS_LINE, MySQLParser.SPOLY_CONTAINS_LINE_NEG, MySQLParser.SPOLY_CONTAINS_LINE_COM, MySQLParser.SPOLY_CONTAINS_LINE_COM_NEG, MySQLParser.SPOLY_OVERLAP_LINE, MySQLParser.SPOLY_OVERLAP_LINE_NEG, MySQLParser.SPOLY_OVERLAP_LINE_COM, MySQLParser.SPOLY_OVERLAP_LINE_COM_NEG, MySQLParser.SPOLY_CONTAINS_ELLIPSE, MySQLParser.SPOLY_CONTAINS_ELLIPSE_NEG, MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM, MySQLParser.SPOLY_CONTAINS_ELLIPSE_COM_NEG, MySQLParser.SELLIPSE_CONTAINS_POLYGON, MySQLParser.SELLIPSE_CONTAINS_POLYGON_NEG, MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM, MySQLParser.SELLIPSE_CONTAINS_POLYGON_COM_NEG, MySQLParser.SPOLY_OVERLAP_ELLIPSE, MySQLParser.SPOLY_OVERLAP_ELLIPSE_NEG, MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM, MySQLParser.SPOLY_OVERLAP_ELLIPSE_COM_NEG, MySQLParser.STRANS_POLY, MySQLParser.STRANS_POLY_INVERSE, MySQLParser.SPOLY_ADD_POINT_AGGR, MySQLParser.SPOLY_AGGR, MySQLParser.SPATH, MySQLParser.SPATH_EQUAL, MySQLParser.SPATH_EQUAL_NEG, MySQLParser.SPATH_OVERLAP_PATH, MySQLParser.SPATH_OVERLAP_PATH_NEG, MySQLParser.SPATH_CONTAINS_POINT, MySQLParser.SPATH_CONTAINS_POINT_NEG, MySQLParser.SPATH_CONTAINS_POINT_COM, MySQLParser.SPATH_CONTAINS_POINT_COM_NEG, MySQLParser.SCIRCLE_CONTAINS_PATH, MySQLParser.SCIRCLE_CONTAINS_PATH_NEG, MySQLParser.SCIRCLE_CONTAINS_PATH_COM, MySQLParser.SCIRCLE_CONTAINS_PATH_COM_NEG, MySQLParser.SCIRCLE_OVERLAP_PATH, MySQLParser.SCIRCLE_OVERLAP_PATH_NEG, MySQLParser.SCIRCLE_OVERLAP_PATH_COM, MySQLParser.SCIRCLE_OVERLAP_PATH_COM_NEG, MySQLParser.SPATH_OVERLAP_LINE, MySQLParser.SPATH_OVERLAP_LINE_NEG, MySQLParser.SPATH_OVERLAP_LINE_COM, MySQLParser.SPATH_OVERLAP_LINE_COM_NEG, MySQLParser.SELLIPSE_CONTAINS_PATH, MySQLParser.SELLIPSE_CONTAINS_PATH_NEG, MySQLParser.SELLIPSE_CONTAINS_PATH_COM, MySQLParser.SELLIPSE_CONTAINS_PATH_COM_NEG, MySQLParser.SELLIPSE_OVERLAP_PATH, MySQLParser.SELLIPSE_OVERLAP_PATH_NEG, MySQLParser.SELLIPSE_OVERLAP_PATH_COM, MySQLParser.SELLIPSE_OVERLAP_PATH_COM_NEG, MySQLParser.SPOLY_CONTAINS_PATH, MySQLParser.SPOLY_CONTAINS_PATH_NEG, MySQLParser.SPOLY_CONTAINS_PATH_COM, MySQLParser.SPOLY_CONTAINS_PATH_COM_NEG, MySQLParser.SPOLY_OVERLAP_PATH, MySQLParser.SPOLY_OVERLAP_PATH_NEG, MySQLParser.SPOLY_OVERLAP_PATH_COM, MySQLParser.SPOLY_OVERLAP_PATH_COM_NEG, MySQLParser.STRANS_PATH, MySQLParser.STRANS_PATH_INVERSE, MySQLParser.SPATH_ADD_POINT_AGGR, MySQLParser.SPATH_AGGR, MySQLParser.SBOX, MySQLParser.SBOX_SW, MySQLParser.SBOX_SE, MySQLParser.SBOX_NW, MySQLParser.SBOX_NE, MySQLParser.SBOX_EQUAL, MySQLParser.SBOX_EQUAL_NEG, MySQLParser.SBOX_CONTAINS_BOX, MySQLParser.SBOX_CONTAINS_BOX_NEG, MySQLParser.SBOX_CONTAINS_BOX_COM, MySQLParser.SBOX_CONTAINS_BOX_COM_NEG, MySQLParser.SBOX_OVERLAP_BOX, MySQLParser.SBOX_OVERLAP_BOX_NEG, MySQLParser.SBOX_CONTAINS_POINT, MySQLParser.SBOX_CONTAINS_POINT_NEG, MySQLParser.SBOX_CONTAINS_POINT_COM, MySQLParser.SBOX_CONTAINS_POINT_COM_NEG, MySQLParser.SBOX_CONTAINS_CIRCLE, MySQLParser.SBOX_CONTAINS_CIRCLE_NEG, MySQLParser.SBOX_CONTAINS_CIRCLE_COM, MySQLParser.SBOX_CONTAINS_CIRCLE_COM_NEG, MySQLParser.SCIRCLE_CONTAINS_BOX, MySQLParser.SCIRCLE_CONTAINS_BOX_NEG, MySQLParser.SCIRCLE_CONTAINS_BOX_COM, MySQLParser.SCIRCLE_CONTAINS_BOX_COM_NEG, MySQLParser.SBOX_OVERLAP_CIRCLE, MySQLParser.SBOX_OVERLAP_CIRCLE_NEG, MySQLParser.SBOX_OVERLAP_CIRCLE_COM, MySQLParser.SBOX_OVERLAP_CIRCLE_COM_NEG, MySQLParser.SBOX_CONTAINS_LINE, MySQLParser.SBOX_CONTAINS_LINE_NEG, MySQLParser.SBOX_CONTAINS_LINE_COM, MySQLParser.SBOX_CONTAINS_LINE_COM_NEG, MySQLParser.SBOX_OVERLAP_LINE, MySQLParser.SBOX_OVERLAP_LINE_NEG, MySQLParser.SBOX_OVERLAP_LINE_COM, MySQLParser.SBOX_OVERLAP_LINE_COM_NEG, MySQLParser.SBOX_CONTAINS_ELLIPSE, MySQLParser.SBOX_CONTAINS_ELLIPSE_NEG, MySQLParser.SBOX_CONTAINS_ELLIPSE_COM, MySQLParser.SBOX_CONTAINS_ELLIPSE_COM_NEG, MySQLParser.SELLIPSE_CONTAINS_BOX, MySQLParser.SELLIPSE_CONTAINS_BOX_NEG, MySQLParser.SELLIPSE_CONTAINS_BOX_COM, MySQLParser.SELLIPSE_CONTAINS_BOX_COM_NEG, MySQLParser.SBOX_OVERLAP_ELLIPSE, MySQLParser.SBOX_OVERLAP_ELLIPSE_NEG, MySQLParser.SBOX_OVERLAP_ELLIPSE_COM, MySQLParser.SBOX_OVERLAP_ELLIPSE_COM_NEG, MySQLParser.SBOX_CONTAINS_POLY, MySQLParser.SBOX_CONTAINS_POLY_NEG, MySQLParser.SBOX_CONTAINS_POLY_COM, MySQLParser.SBOX_CONTAINS_POLY_COM_NEG, MySQLParser.SPOLY_CONTAINS_BOX, MySQLParser.SPOLY_CONTAINS_BOX_NEG, MySQLParser.SPOLY_CONTAINS_BOX_COM, MySQLParser.SPOLY_CONTAINS_BOX_COM_NEG, MySQLParser.SBOX_OVERLAP_POLY, MySQLParser.SBOX_OVERLAP_POLY_NEG, MySQLParser.SBOX_OVERLAP_POLY_COM, MySQLParser.SBOX_OVERLAP_POLY_COM_NEG, MySQLParser.SBOX_CONTAINS_PATH, MySQLParser.SBOX_CONTAINS_PATH_NEG, MySQLParser.SBOX_CONTAINS_PATH_COM, MySQLParser.SBOX_CONTAINS_PATH_COM_NEG, MySQLParser.SBOX_OVERLAP_PATH, MySQLParser.SBOX_OVERLAP_PATH_NEG, MySQLParser.SBOX_OVERLAP_PATH_COM, MySQLParser.SBOX_OVERLAP_PATH_COM_NEG, MySQLParser.STRRPOS, MySQLParser.IDLE, MySQLParser.ANGDIST, MySQLParser.HILBERTKEY, MySQLParser.COORDFROMHILBERTKEY, MySQLParser.SUM_OF_SQUARES, MySQLParser.PARTITADD_SUM_OF_SQARES, MySQLParser.GAIA_HEALPIX, MySQLParser.LPAREN, MySQLParser.PLUS, MySQLParser.MINUS, MySQLParser.NEGATION, MySQLParser.INTEGER_NUM, MySQLParser.HEX_DIGIT, MySQLParser.BIT_NUM, MySQLParser.REAL_NUMBER, MySQLParser.TEXT_STRING, MySQLParser.ID, MySQLParser.USER_VAR]:
                self.state = 724
                self.displayed_column()
                self.state = 729
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==MySQLParser.COMMA:
                    self.state = 725
                    self.match(MySQLParser.COMMA)
                    self.state = 726
                    self.displayed_column()
                    self.state = 731
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [MySQLParser.ASTERISK]:
                self.state = 732
                self.match(MySQLParser.ASTERISK)
                self.state = 742
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.COMMA:
                    self.state = 733
                    self.match(MySQLParser.COMMA)
                    self.state = 734
                    self.displayed_column()
                    self.state = 739
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while _la==MySQLParser.COMMA:
                        self.state = 735
                        self.match(MySQLParser.COMMA)
                        self.state = 736
                        self.displayed_column()
                        self.state = 741
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)



                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Select_statementContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Select_statementContext, self).__init__(parent, invokingState)
            self.parser = parser

        def select_expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Select_expressionContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Select_expressionContext,i)


        def UNION_SYM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.UNION_SYM)
            else:
                return self.getToken(MySQLParser.UNION_SYM, i)

        def ALL(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.ALL)
            else:
                return self.getToken(MySQLParser.ALL, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_select_statement

        def enterRule(self, listener):
            if hasattr(listener, "enterSelect_statement"):
                listener.enterSelect_statement(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSelect_statement"):
                listener.exitSelect_statement(self)




    def select_statement(self):

        localctx = MySQLParser.Select_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 134, self.RULE_select_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 746
            self.select_expression()
            self.state = 754
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MySQLParser.UNION_SYM:
                self.state = 747
                self.match(MySQLParser.UNION_SYM)
                self.state = 749
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.ALL:
                    self.state = 748
                    self.match(MySQLParser.ALL)


                self.state = 751
                self.select_expression()
                self.state = 756
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Simple_exprContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Simple_exprContext, self).__init__(parent, invokingState)
            self.parser = parser

        def literal_value(self):
            return self.getTypedRuleContext(MySQLParser.Literal_valueContext,0)


        def expression_list(self):
            return self.getTypedRuleContext(MySQLParser.Expression_listContext,0)


        def column_spec(self):
            return self.getTypedRuleContext(MySQLParser.Column_specContext,0)


        def function_call(self):
            return self.getTypedRuleContext(MySQLParser.Function_callContext,0)


        def USER_VAR(self):
            return self.getToken(MySQLParser.USER_VAR, 0)

        def ROW_SYM(self):
            return self.getToken(MySQLParser.ROW_SYM, 0)

        def subquery(self):
            return self.getTypedRuleContext(MySQLParser.SubqueryContext,0)


        def EXISTS(self):
            return self.getToken(MySQLParser.EXISTS, 0)

        def interval_expr(self):
            return self.getTypedRuleContext(MySQLParser.Interval_exprContext,0)


        def match_against_statement(self):
            return self.getTypedRuleContext(MySQLParser.Match_against_statementContext,0)


        def case_when_statement(self):
            return self.getTypedRuleContext(MySQLParser.Case_when_statementContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_simple_expr

        def enterRule(self, listener):
            if hasattr(listener, "enterSimple_expr"):
                listener.enterSimple_expr(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSimple_expr"):
                listener.exitSimple_expr(self)




    def simple_expr(self):

        localctx = MySQLParser.Simple_exprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 136, self.RULE_simple_expr)
        try:
            self.state = 770
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,92,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 757
                self.literal_value()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 758
                self.expression_list()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 759
                self.column_spec()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 760
                self.function_call()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 761
                self.match(MySQLParser.USER_VAR)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 762
                self.match(MySQLParser.ROW_SYM)
                self.state = 763
                self.expression_list()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 764
                self.subquery()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 765
                self.match(MySQLParser.EXISTS)
                self.state = 766
                self.subquery()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 767
                self.interval_expr()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 768
                self.match_against_statement()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 769
                self.case_when_statement()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class SubqueryContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.SubqueryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(MySQLParser.LPAREN, 0)

        def select_statement(self):
            return self.getTypedRuleContext(MySQLParser.Select_statementContext,0)


        def RPAREN(self):
            return self.getToken(MySQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_subquery

        def enterRule(self, listener):
            if hasattr(listener, "enterSubquery"):
                listener.enterSubquery(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSubquery"):
                listener.exitSubquery(self)




    def subquery(self):

        localctx = MySQLParser.SubqueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 138, self.RULE_subquery)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 772
            self.match(MySQLParser.LPAREN)
            self.state = 773
            self.select_statement()
            self.state = 774
            self.match(MySQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_atomContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Table_atomContext, self).__init__(parent, invokingState)
            self.parser = parser

        def table_spec(self):
            return self.getTypedRuleContext(MySQLParser.Table_specContext,0)


        def partition_clause(self):
            return self.getTypedRuleContext(MySQLParser.Partition_clauseContext,0)


        def alias(self):
            return self.getTypedRuleContext(MySQLParser.AliasContext,0)


        def index_hint_list(self):
            return self.getTypedRuleContext(MySQLParser.Index_hint_listContext,0)


        def subquery(self):
            return self.getTypedRuleContext(MySQLParser.SubqueryContext,0)


        def LPAREN(self):
            return self.getToken(MySQLParser.LPAREN, 0)

        def table_references(self):
            return self.getTypedRuleContext(MySQLParser.Table_referencesContext,0)


        def RPAREN(self):
            return self.getToken(MySQLParser.RPAREN, 0)

        def OJ_SYM(self):
            return self.getToken(MySQLParser.OJ_SYM, 0)

        def table_reference(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Table_referenceContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Table_referenceContext,i)


        def LEFT(self):
            return self.getToken(MySQLParser.LEFT, 0)

        def OUTER(self):
            return self.getToken(MySQLParser.OUTER, 0)

        def JOIN_SYM(self):
            return self.getToken(MySQLParser.JOIN_SYM, 0)

        def ON(self):
            return self.getToken(MySQLParser.ON, 0)

        def expression(self):
            return self.getTypedRuleContext(MySQLParser.ExpressionContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_table_atom

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_atom"):
                listener.enterTable_atom(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_atom"):
                listener.exitTable_atom(self)




    def table_atom(self):

        localctx = MySQLParser.Table_atomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 140, self.RULE_table_atom)
        self._la = 0 # Token type
        try:
            self.state = 802
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,96,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 776
                self.table_spec()
                self.state = 778
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,93,self._ctx)
                if la_ == 1:
                    self.state = 777
                    self.partition_clause()


                self.state = 781
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.AS_SYM or _la==MySQLParser.ID:
                    self.state = 780
                    self.alias()


                self.state = 784
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.FORCE_SYM or _la==MySQLParser.IGNORE_SYM or _la==MySQLParser.USE_SYM:
                    self.state = 783
                    self.index_hint_list()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 786
                self.subquery()
                self.state = 787
                self.alias()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 789
                self.match(MySQLParser.LPAREN)
                self.state = 790
                self.table_references()
                self.state = 791
                self.match(MySQLParser.RPAREN)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 793
                self.match(MySQLParser.OJ_SYM)
                self.state = 794
                self.table_reference()
                self.state = 795
                self.match(MySQLParser.LEFT)
                self.state = 796
                self.match(MySQLParser.OUTER)
                self.state = 797
                self.match(MySQLParser.JOIN_SYM)
                self.state = 798
                self.table_reference()
                self.state = 799
                self.match(MySQLParser.ON)
                self.state = 800
                self.expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Table_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(MySQLParser.ID, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_table_name

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_name"):
                listener.enterTable_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_name"):
                listener.exitTable_name(self)




    def table_name(self):

        localctx = MySQLParser.Table_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 142, self.RULE_table_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 804
            self.match(MySQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_factor1Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Table_factor1Context, self).__init__(parent, invokingState)
            self.parser = parser

        def table_factor2(self):
            return self.getTypedRuleContext(MySQLParser.Table_factor2Context,0)


        def JOIN_SYM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.JOIN_SYM)
            else:
                return self.getToken(MySQLParser.JOIN_SYM, i)

        def table_atom(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Table_atomContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Table_atomContext,i)


        def join_condition(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Join_conditionContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Join_conditionContext,i)


        def INNER_SYM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.INNER_SYM)
            else:
                return self.getToken(MySQLParser.INNER_SYM, i)

        def CROSS(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.CROSS)
            else:
                return self.getToken(MySQLParser.CROSS, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_table_factor1

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_factor1"):
                listener.enterTable_factor1(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_factor1"):
                listener.exitTable_factor1(self)




    def table_factor1(self):

        localctx = MySQLParser.Table_factor1Context(self, self._ctx, self.state)
        self.enterRule(localctx, 144, self.RULE_table_factor1)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 806
            self.table_factor2()
            self.state = 817
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MySQLParser.CROSS or _la==MySQLParser.INNER_SYM or _la==MySQLParser.JOIN_SYM:
                self.state = 808
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.CROSS or _la==MySQLParser.INNER_SYM:
                    self.state = 807
                    _la = self._input.LA(1)
                    if not(_la==MySQLParser.CROSS or _la==MySQLParser.INNER_SYM):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()


                self.state = 810
                self.match(MySQLParser.JOIN_SYM)
                self.state = 811
                self.table_atom()
                self.state = 813
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,98,self._ctx)
                if la_ == 1:
                    self.state = 812
                    self.join_condition()


                self.state = 819
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_factor2Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Table_factor2Context, self).__init__(parent, invokingState)
            self.parser = parser

        def table_factor3(self):
            return self.getTypedRuleContext(MySQLParser.Table_factor3Context,0)


        def STRAIGHT_JOIN(self):
            return self.getToken(MySQLParser.STRAIGHT_JOIN, 0)

        def table_atom(self):
            return self.getTypedRuleContext(MySQLParser.Table_atomContext,0)


        def ON(self):
            return self.getToken(MySQLParser.ON, 0)

        def expression(self):
            return self.getTypedRuleContext(MySQLParser.ExpressionContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_table_factor2

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_factor2"):
                listener.enterTable_factor2(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_factor2"):
                listener.exitTable_factor2(self)




    def table_factor2(self):

        localctx = MySQLParser.Table_factor2Context(self, self._ctx, self.state)
        self.enterRule(localctx, 146, self.RULE_table_factor2)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 820
            self.table_factor3()
            self.state = 827
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.STRAIGHT_JOIN:
                self.state = 821
                self.match(MySQLParser.STRAIGHT_JOIN)
                self.state = 822
                self.table_atom()
                self.state = 825
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,100,self._ctx)
                if la_ == 1:
                    self.state = 823
                    self.match(MySQLParser.ON)
                    self.state = 824
                    self.expression()




        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_factor3Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Table_factor3Context, self).__init__(parent, invokingState)
            self.parser = parser

        def table_factor4(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Table_factor4Context)
            else:
                return self.getTypedRuleContext(MySQLParser.Table_factor4Context,i)


        def JOIN_SYM(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.JOIN_SYM)
            else:
                return self.getToken(MySQLParser.JOIN_SYM, i)

        def join_condition(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Join_conditionContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Join_conditionContext,i)


        def LEFT(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.LEFT)
            else:
                return self.getToken(MySQLParser.LEFT, i)

        def RIGHT(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.RIGHT)
            else:
                return self.getToken(MySQLParser.RIGHT, i)

        def OUTER(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.OUTER)
            else:
                return self.getToken(MySQLParser.OUTER, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_table_factor3

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_factor3"):
                listener.enterTable_factor3(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_factor3"):
                listener.exitTable_factor3(self)




    def table_factor3(self):

        localctx = MySQLParser.Table_factor3Context(self, self._ctx, self.state)
        self.enterRule(localctx, 148, self.RULE_table_factor3)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 829
            self.table_factor4()
            self.state = 840
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,103,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 830
                    _la = self._input.LA(1)
                    if not(_la==MySQLParser.LEFT or _la==MySQLParser.RIGHT):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 832
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==MySQLParser.OUTER:
                        self.state = 831
                        self.match(MySQLParser.OUTER)


                    self.state = 834
                    self.match(MySQLParser.JOIN_SYM)
                    self.state = 835
                    self.table_factor4()
                    self.state = 836
                    self.join_condition() 
                self.state = 842
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,103,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_factor4Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Table_factor4Context, self).__init__(parent, invokingState)
            self.parser = parser

        def table_atom(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Table_atomContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Table_atomContext,i)


        def NATURAL(self):
            return self.getToken(MySQLParser.NATURAL, 0)

        def JOIN_SYM(self):
            return self.getToken(MySQLParser.JOIN_SYM, 0)

        def LEFT(self):
            return self.getToken(MySQLParser.LEFT, 0)

        def RIGHT(self):
            return self.getToken(MySQLParser.RIGHT, 0)

        def OUTER(self):
            return self.getToken(MySQLParser.OUTER, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_table_factor4

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_factor4"):
                listener.enterTable_factor4(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_factor4"):
                listener.exitTable_factor4(self)




    def table_factor4(self):

        localctx = MySQLParser.Table_factor4Context(self, self._ctx, self.state)
        self.enterRule(localctx, 150, self.RULE_table_factor4)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 843
            self.table_atom()
            self.state = 853
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MySQLParser.NATURAL:
                self.state = 844
                self.match(MySQLParser.NATURAL)
                self.state = 849
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MySQLParser.LEFT or _la==MySQLParser.RIGHT:
                    self.state = 845
                    _la = self._input.LA(1)
                    if not(_la==MySQLParser.LEFT or _la==MySQLParser.RIGHT):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 847
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==MySQLParser.OUTER:
                        self.state = 846
                        self.match(MySQLParser.OUTER)




                self.state = 851
                self.match(MySQLParser.JOIN_SYM)
                self.state = 852
                self.table_atom()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_referenceContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Table_referenceContext, self).__init__(parent, invokingState)
            self.parser = parser

        def table_factor1(self):
            return self.getTypedRuleContext(MySQLParser.Table_factor1Context,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_table_reference

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_reference"):
                listener.enterTable_reference(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_reference"):
                listener.exitTable_reference(self)




    def table_reference(self):

        localctx = MySQLParser.Table_referenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 152, self.RULE_table_reference)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 855
            self.table_factor1()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_referencesContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Table_referencesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def table_reference(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MySQLParser.Table_referenceContext)
            else:
                return self.getTypedRuleContext(MySQLParser.Table_referenceContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(MySQLParser.COMMA)
            else:
                return self.getToken(MySQLParser.COMMA, i)

        def getRuleIndex(self):
            return MySQLParser.RULE_table_references

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_references"):
                listener.enterTable_references(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_references"):
                listener.exitTable_references(self)




    def table_references(self):

        localctx = MySQLParser.Table_referencesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 154, self.RULE_table_references)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 857
            self.table_reference()
            self.state = 862
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MySQLParser.COMMA:
                self.state = 858
                self.match(MySQLParser.COMMA)
                self.state = 859
                self.table_reference()
                self.state = 864
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_specContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Table_specContext, self).__init__(parent, invokingState)
            self.parser = parser

        def table_name(self):
            return self.getTypedRuleContext(MySQLParser.Table_nameContext,0)


        def schema_name(self):
            return self.getTypedRuleContext(MySQLParser.Schema_nameContext,0)


        def DOT(self):
            return self.getToken(MySQLParser.DOT, 0)

        def getRuleIndex(self):
            return MySQLParser.RULE_table_spec

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_spec"):
                listener.enterTable_spec(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_spec"):
                listener.exitTable_spec(self)




    def table_spec(self):

        localctx = MySQLParser.Table_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 156, self.RULE_table_spec)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 868
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,108,self._ctx)
            if la_ == 1:
                self.state = 865
                self.schema_name()
                self.state = 866
                self.match(MySQLParser.DOT)


            self.state = 870
            self.table_name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Where_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MySQLParser.Where_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WHERE(self):
            return self.getToken(MySQLParser.WHERE, 0)

        def expression(self):
            return self.getTypedRuleContext(MySQLParser.ExpressionContext,0)


        def getRuleIndex(self):
            return MySQLParser.RULE_where_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterWhere_clause"):
                listener.enterWhere_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitWhere_clause"):
                listener.exitWhere_clause(self)




    def where_clause(self):

        localctx = MySQLParser.Where_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 158, self.RULE_where_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 872
            self.match(MySQLParser.WHERE)
            self.state = 873
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





