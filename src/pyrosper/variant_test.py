import pytest
from .variant import Variant
from .symbol import Symbol


class TestVariant:
    """Tests for the Variant class"""
    
    def test_init(self):
        """Test Variant initialization"""
        key = Symbol("test_key")
        picks = {key: "test_value"}
        variant = Variant("test_variant", picks)
        assert variant.name == "test_variant"
        assert variant.picks == picks
    
    def test_get_pick_success(self):
        """Test get_pick returns correct value"""
        picks = {"test_symbol": "test_value"}
        variant = Variant("test_variant", picks)
        result = variant.get_pick("test_symbol")
        assert result == "test_value"
    
    def test_get_pick_with_symbol_object(self):
        """Test get_pick works with Symbol objects"""
        symbol = Symbol("test_symbol")
        picks = {symbol: "test_value"}
        variant = Variant("test_variant", picks)
        result = variant.get_pick(symbol)
        assert result == "test_value"
    
    def test_get_pick_key_error(self):
        """Test get_pick raises KeyError when symbol not found"""
        picks = {"existing_symbol": "test_value"}
        variant = Variant("test_variant", picks)
        with pytest.raises(KeyError):
            variant.get_pick("non_existent_symbol")
    
    def test_get_pick_empty_picks(self):
        """Test get_pick with empty picks dictionary"""
        variant = Variant("test_variant", {})
        with pytest.raises(KeyError):
            variant.get_pick("any_symbol")
    
    def test_variant_with_complex_objects(self):
        """Test Variant with complex objects as picks"""
        class ComplexObject:
            def __init__(self, value):
                self.value = value
        
        obj1 = ComplexObject("value1")
        obj2 = ComplexObject("value2")
        picks = {"obj1": obj1, "obj2": obj2}
        variant = Variant("complex_variant", picks)
        
        assert variant.get_pick("obj1") == obj1
        assert variant.get_pick("obj2") == obj2
        assert variant.get_pick("obj1").value == "value1" 