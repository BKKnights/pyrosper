"""
Test demonstrating how to use PyrosperContext.
"""

import asyncio
import pytest
from unittest.mock import Mock
from .context import Context, get_current, context_storage, instance_storage, context


class TestContext:
    """Tests for the Context class"""
    
    def test_context_init(self):
        """Test Context initialization"""
        ctx = Context()
        assert ctx.token is None
        assert ctx.instance_token is None
        assert ctx.pyrosper_instance is None
    
    def test_setup_context_not_implemented(self):
        """Test that setup_context raises NotImplementedError by default"""
        ctx = Context()
        with pytest.raises(NotImplementedError, match="Class must implement setup_context\\(\\)"):
            ctx.setup_context()
    
    def test_teardown_context_default(self):
        """Test that teardown_context doesn't raise by default"""
        ctx = Context()
        # Should not raise any exception
        ctx.teardown_context()
    
    def test_context_as_context_manager(self):
        """Test Context as context manager"""
        mock_pyrosper = Mock()
        
        class TestContext(Context):
            def setup_context(self):
                return mock_pyrosper
        
        ctx = TestContext()
        with ctx as pyrosper:
            assert pyrosper == mock_pyrosper
            # Check that context variables are set
            assert context_storage.get() == f"pyrosper_context_{id(ctx)}"
            assert instance_storage.get() == mock_pyrosper
    
    def test_context_as_context_manager_with_exception(self):
        """Test Context as context manager handles exceptions properly"""
        mock_pyrosper = Mock()
        
        class TestContext(Context):
            def setup_context(self):
                return mock_pyrosper
        
        with pytest.raises(ValueError):
            with TestContext() as pyrosper:
                raise ValueError("test exception")
        
        # Check that context variables are reset
        assert context_storage.get() == "unknown"
        assert instance_storage.get() is None
    
    def test_context_teardown_called(self):
        """Test that teardown_context is called when exiting context"""
        mock_pyrosper = Mock()
        teardown_called = False
        
        class TestContext(Context):
            def setup_context(self):
                return mock_pyrosper
            
            def teardown_context(self):
                nonlocal teardown_called
                teardown_called = True
        
        with TestContext():
            pass
        
        assert teardown_called
    
    def test_context_multiple_instances(self):
        """Test that multiple Context instances work independently"""
        mock_pyrosper1 = Mock()
        mock_pyrosper2 = Mock()
        
        class TestContext(Context):
            def __init__(self, pyrosper_instance):
                super().__init__()
                self.pyrosper_instance = pyrosper_instance
            
            def setup_context(self):
                return self.pyrosper_instance
        
        ctx1 = TestContext(mock_pyrosper1)
        ctx2 = TestContext(mock_pyrosper2)
        
        with ctx1 as pyrosper1:
            assert pyrosper1 == mock_pyrosper1
            with ctx2 as pyrosper2:
                assert pyrosper2 == mock_pyrosper2
                # Inner context should override outer
                assert instance_storage.get() == mock_pyrosper2
            
            # After inner context exits, should be back to outer
            assert instance_storage.get() == mock_pyrosper1
        
        # After both contexts exit, should be reset
        assert context_storage.get() == "unknown"
        assert instance_storage.get() is None


class TestGetCurrent:
    """Tests for the get_current function"""
    
    def test_get_current_success(self):
        """Test get_current returns the current pyrosper instance"""
        mock_pyrosper = Mock()
        
        # Set the instance in context
        token = instance_storage.set(mock_pyrosper)
        try:
            result = get_current()
            assert result == mock_pyrosper
        finally:
            instance_storage.reset(token)
    
    def test_get_current_no_instance(self):
        """Test get_current raises RuntimeError when no instance is set"""
        # Ensure no instance is set
        assert instance_storage.get() is None
        
        with pytest.raises(RuntimeError, match="No pyrosper instance found in context"):
            get_current()
    
    def test_get_current_with_none_instance(self):
        """Test get_current raises RuntimeError when instance is None"""
        # Set None as the instance
        token = instance_storage.set(None)
        try:
            with pytest.raises(RuntimeError, match="No pyrosper instance found in context"):
                get_current()
        finally:
            instance_storage.reset(token)


class TestContextDecorator:
    """Tests for the context decorator"""
    
    def test_context_sync_function(self):
        """Test context decorator with synchronous functions"""
        
        @context()
        def test_function():
            return "test_result"
        
        # Test that the function works normally
        result = test_function()
        assert result == "test_result"
        
        # Test that the function preserves its name
        assert test_function.__name__ == "test_function"
    
    def test_context_async_function(self):
        """Test context decorator with asynchronous functions"""
        
        @context()
        async def test_async_function():
            return "async_test_result"
        
        # Test that the async function works normally
        async def run_test():
            result = await test_async_function()
            assert result == "async_test_result"
            # Test that the function preserves its name
            assert test_async_function.__name__ == "test_async_function"
        
        asyncio.run(run_test())
    
    def test_context_with_exception(self):
        """Test context decorator properly handles exceptions"""
        
        @context()
        def test_function_with_exception():
            raise ValueError("test exception")
        
        with pytest.raises(ValueError, match="test exception"):
            test_function_with_exception()
    
    def test_context_async_with_exception(self):
        """Test context decorator properly handles async exceptions"""
        
        @context()
        async def test_async_function_with_exception():
            raise ValueError("async test exception")
        
        async def run_test():
            with pytest.raises(ValueError, match="async test exception"):
                await test_async_function_with_exception()
        
        asyncio.run(run_test())
    
    def test_context_preserves_function_metadata(self):
        """Test that context decorator preserves function metadata"""
        
        @context()
        def test_function_with_docstring():
            """This is a test function with a docstring."""
            return "result"
        
        assert test_function_with_docstring.__doc__ == "This is a test function with a docstring."
        assert test_function_with_docstring.__name__ == "test_function_with_docstring"
    
    def test_context_async_preserves_function_metadata(self):
        """Test that context decorator preserves async function metadata"""
        
        @context()
        async def test_async_function_with_docstring():
            """This is an async test function with a docstring."""
            return "async_result"
        
        assert test_async_function_with_docstring.__doc__ == "This is an async test function with a docstring."
        assert test_async_function_with_docstring.__name__ == "test_async_function_with_docstring"