from .symbol import Symbol


class TestSymbol:
    """Tests for the Symbol class"""
    
    def test_init(self):
        """Test Symbol initialization"""
        symbol = Symbol("test_description")
        assert symbol.description == "test_description"
        assert hasattr(symbol, 'unique_id')
        assert symbol.unique_id is not None
    
    def test_unique_id_uniqueness(self):
        """Test that each Symbol has a unique ID"""
        symbol1 = Symbol("description1")
        symbol2 = Symbol("description2")
        symbol3 = Symbol("description1")  # Same description, different object
        
        assert symbol1.unique_id != symbol2.unique_id
        assert symbol1.unique_id != symbol3.unique_id
        assert symbol2.unique_id != symbol3.unique_id
    
    def test_repr(self):
        """Test Symbol string representation"""
        symbol = Symbol("test_description")
        expected_repr = "Symbol(test_description)"
        assert repr(symbol) == expected_repr
    
    def test_empty_description(self):
        """Test Symbol with empty description"""
        symbol = Symbol("")
        assert symbol.description == ""
        assert repr(symbol) == "Symbol()"
    

    
    def test_symbol_as_dict_key(self):
        """Test that Symbol can be used as dictionary key"""
        symbol1 = Symbol("key1")
        symbol2 = Symbol("key2")
        
        test_dict = {symbol1: "value1", symbol2: "value2"}
        
        assert test_dict[symbol1] == "value1"
        assert test_dict[symbol2] == "value2"
    
    def test_symbol_hashability(self):
        """Test that Symbol objects are hashable"""
        symbol = Symbol("test")
        # Should not raise TypeError
        hash(symbol)
        
        # Should be able to add to set
        symbol_set = {symbol}
        assert symbol in symbol_set 