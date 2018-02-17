# Generated from src/queryparser/adql/ADQLParser.g4 by ANTLR 4.7
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by ADQLParser.

class ADQLParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ADQLParser#approximate_numeric_literal.
    def visitApproximate_numeric_literal(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#area.
    def visitArea(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#as_clause.
    def visitAs_clause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#between_predicate.
    def visitBetween_predicate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#bitwise_and.
    def visitBitwise_and(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#bitwise_not.
    def visitBitwise_not(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#bitwise_or.
    def visitBitwise_or(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#bitwise_xor.
    def visitBitwise_xor(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#boolean_factor.
    def visitBoolean_factor(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#boolean_literal.
    def visitBoolean_literal(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#boolean_primary.
    def visitBoolean_primary(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#boolean_term.
    def visitBoolean_term(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#boolean_value_expression.
    def visitBoolean_value_expression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#box.
    def visitBox(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#catalog_name.
    def visitCatalog_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#centroid.
    def visitCentroid(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#char_function.
    def visitChar_function(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#character_string_literal.
    def visitCharacter_string_literal(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#character_value_expression.
    def visitCharacter_value_expression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#circle.
    def visitCircle(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#column_name.
    def visitColumn_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#column_name_list.
    def visitColumn_name_list(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#column_reference.
    def visitColumn_reference(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#comp_op.
    def visitComp_op(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#comparison_predicate.
    def visitComparison_predicate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#concatenation_operator.
    def visitConcatenation_operator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#contains.
    def visitContains(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#coord_sys.
    def visitCoord_sys(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#coord_value.
    def visitCoord_value(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#coord1.
    def visitCoord1(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#coord2.
    def visitCoord2(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#coordinate1.
    def visitCoordinate1(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#coordinate2.
    def visitCoordinate2(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#coordinates.
    def visitCoordinates(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#correlation_name.
    def visitCorrelation_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#correlation_specification.
    def visitCorrelation_specification(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#delimited_identifier.
    def visitDelimited_identifier(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#derived_column.
    def visitDerived_column(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#derived_table.
    def visitDerived_table(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#distance.
    def visitDistance(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#exact_numeric_literal.
    def visitExact_numeric_literal(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#exists_predicate.
    def visitExists_predicate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#extract_coordsys.
    def visitExtract_coordsys(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#factor.
    def visitFactor(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#from_clause.
    def visitFrom_clause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#general_literal.
    def visitGeneral_literal(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#general_set_function.
    def visitGeneral_set_function(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#geometry_value_expression.
    def visitGeometry_value_expression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#group_by_clause.
    def visitGroup_by_clause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#grouping_column_reference.
    def visitGrouping_column_reference(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#grouping_column_reference_list.
    def visitGrouping_column_reference_list(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#having_clause.
    def visitHaving_clause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#identifier.
    def visitIdentifier(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#in_predicate.
    def visitIn_predicate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#in_predicate_value.
    def visitIn_predicate_value(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#in_value_list.
    def visitIn_value_list(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#intersects.
    def visitIntersects(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#join_column_list.
    def visitJoin_column_list(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#join_condition.
    def visitJoin_condition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#join_specification.
    def visitJoin_specification(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#join_type.
    def visitJoin_type(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#joined_table.
    def visitJoined_table(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#like_predicate.
    def visitLike_predicate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#match_value.
    def visitMatch_value(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#math_function.
    def visitMath_function(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#named_columns_join.
    def visitNamed_columns_join(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#non_join_query_expression.
    def visitNon_join_query_expression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#non_join_query_primary.
    def visitNon_join_query_primary(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#non_join_query_term.
    def visitNon_join_query_term(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#non_predicate_geometry_function.
    def visitNon_predicate_geometry_function(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#null_predicate.
    def visitNull_predicate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#numeric_geometry_function.
    def visitNumeric_geometry_function(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#numeric_primary.
    def visitNumeric_primary(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#numeric_value_expression.
    def visitNumeric_value_expression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#numeric_value_function.
    def visitNumeric_value_function(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#offset_clause.
    def visitOffset_clause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#order_by_clause.
    def visitOrder_by_clause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#ordering_specification.
    def visitOrdering_specification(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#outer_join_type.
    def visitOuter_join_type(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#pattern.
    def visitPattern(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#point.
    def visitPoint(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#polygon.
    def visitPolygon(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#predicate.
    def visitPredicate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#predicate_geometry_function.
    def visitPredicate_geometry_function(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#qualifier.
    def visitQualifier(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#query_expression.
    def visitQuery_expression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#query_name.
    def visitQuery_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#query.
    def visitQuery(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#query_specification.
    def visitQuery_specification(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#query_term.
    def visitQuery_term(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#radius.
    def visitRadius(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#region.
    def visitRegion(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#regular_identifier.
    def visitRegular_identifier(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#schema_name.
    def visitSchema_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#search_condition.
    def visitSearch_condition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#select_list.
    def visitSelect_list(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#select_query.
    def visitSelect_query(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#select_sublist.
    def visitSelect_sublist(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#set_function_specification.
    def visitSet_function_specification(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#set_function_type.
    def visitSet_function_type(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#set_limit.
    def visitSet_limit(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#set_quantifier.
    def visitSet_quantifier(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#sign.
    def visitSign(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#signed_integer.
    def visitSigned_integer(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#sort_key.
    def visitSort_key(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#sort_specification.
    def visitSort_specification(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#sort_specification_list.
    def visitSort_specification_list(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#string_geometry_function.
    def visitString_geometry_function(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#string_value_expression.
    def visitString_value_expression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#string_value_function.
    def visitString_value_function(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#subquery.
    def visitSubquery(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#table_expression.
    def visitTable_expression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#table_name.
    def visitTable_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#table_reference.
    def visitTable_reference(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#table_subquery.
    def visitTable_subquery(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#term.
    def visitTerm(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#trig_function.
    def visitTrig_function(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#unqualified_schema_name.
    def visitUnqualified_schema_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#unsigned_decimal.
    def visitUnsigned_decimal(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#unsigned_hexadecimal.
    def visitUnsigned_hexadecimal(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#unsigned_literal.
    def visitUnsigned_literal(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#unsigned_numeric_literal.
    def visitUnsigned_numeric_literal(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#unsigned_value_specification.
    def visitUnsigned_value_specification(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#user_defined_function.
    def visitUser_defined_function(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#user_defined_function_name.
    def visitUser_defined_function_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#user_defined_function_param.
    def visitUser_defined_function_param(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#value_expression.
    def visitValue_expression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#value_expression_primary.
    def visitValue_expression_primary(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#where_clause.
    def visitWhere_clause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ADQLParser#with_query.
    def visitWith_query(self, ctx):
        return self.visitChildren(ctx)


