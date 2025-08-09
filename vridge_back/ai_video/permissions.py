"""
Custom permissions for AI Video Generation
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'story'):
            return obj.story.user == request.user
        elif hasattr(obj, 'scene'):
            return obj.scene.story.user == request.user
        
        return False


class IsStoryOwner(permissions.BasePermission):
    """
    Permission to check if user owns the story
    """
    
    def has_permission(self, request, view):
        # Authenticated users only
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if user owns the story
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'story'):
            return obj.story.user == request.user
        elif hasattr(obj, 'scene'):
            return obj.scene.story.user == request.user
        
        return False


class CanTransitionStory(permissions.BasePermission):
    """
    Permission to check if user can transition story status
    """
    
    def has_object_permission(self, request, view, obj):
        # Must be owner
        if obj.user != request.user:
            return False
        
        # Check if transition is allowed based on current status
        if view.action == 'transition':
            new_status = request.data.get('new_status')
            if new_status:
                return obj.can_transition_to(new_status)
        
        return True


class IsJobOwner(permissions.BasePermission):
    """
    Permission to check if user owns the job (through story/scene)
    """
    
    def has_object_permission(self, request, view, obj):
        if obj.story:
            return obj.story.user == request.user
        elif obj.scene:
            return obj.scene.story.user == request.user
        
        return False