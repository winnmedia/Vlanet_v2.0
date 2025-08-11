'use client';

import React, { useState, useRef, useCallback } from 'react';
import { useAuth } from '@/contexts/auth.context';
import { 
  User, 
  Upload, 
  Edit3, 
  Save, 
  X, 
  Camera, 
  Mail, 
  Phone, 
  Building,
  Calendar,
  Shield,
  Settings,
  Key,
  Trash2,
  AlertTriangle,
  Search
} from 'lucide-react';
import type { User as UserType } from '@/types';

interface EditableFieldProps {
  label: string;
  value: string;
  isEditing: boolean;
  onEdit: (value: string) => void;
  placeholder?: string;
  type?: 'text' | 'email' | 'tel';
  multiline?: boolean;
}

function EditableField({ 
  label, 
  value, 
  isEditing, 
  onEdit, 
  placeholder, 
  type = 'text',
  multiline = false 
}: EditableFieldProps) {
  const [editValue, setEditValue] = useState(value);

  const handleSave = () => {
    onEdit(editValue);
  };

  const handleCancel = () => {
    setEditValue(value);
    onEdit('');
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      {isEditing ? (
        <div className="flex gap-2">
          {multiline ? (
            <textarea
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              placeholder={placeholder}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={3}
            />
          ) : (
            <input
              type={type}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              placeholder={placeholder}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          )}
          <button
            onClick={handleSave}
            className="p-2 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-lg"
            title=""
          >
            <Save className="h-4 w-4" />
          </button>
          <button
            onClick={handleCancel}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-50 rounded-lg"
            title=""
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <span className="text-gray-900">
            {value || <span className="text-gray-400">{placeholder}</span>}
          </span>
          <button
            onClick={() => onEdit(value)}
            className="p-1 text-gray-400 hover:text-blue-600 hover:bg-white rounded"
            title=""
          >
            <Edit3 className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}

interface ProfileImageUploadProps {
  currentImage?: string | null;
  onImageChange: (file: File | null) => void;
  isUploading: boolean;
}

function ProfileImageUpload({ currentImage, onImageChange, isUploading }: ProfileImageUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      //    (5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('  5MB   .');
        return;
      }

      //   
      if (!file.type.startsWith('image/')) {
        alert('   .');
        return;
      }

      onImageChange(file);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <div className="relative group">
        <div 
          className="w-32 h-32 rounded-full bg-gray-100 border-2 border-gray-200 flex items-center justify-center overflow-hidden cursor-pointer hover:border-blue-300 transition-colors"
          onClick={handleImageClick}
        >
          {currentImage ? (
            <img 
              src={currentImage} 
              alt=" " 
              className="w-full h-full object-cover"
            />
          ) : (
            <User className="h-16 w-16 text-gray-400" />
          )}
          
          {/*   */}
          <div className="absolute inset-0 bg-black bg-opacity-40 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <Camera className="h-6 w-6 text-white" />
          </div>

          {/*   */}
          {isUploading && (
            <div className="absolute inset-0 bg-white bg-opacity-80 rounded-full flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent"></div>
            </div>
          )}
        </div>
        
        {/*   */}
        <button
          onClick={handleImageClick}
          className="absolute -bottom-1 -right-1 p-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors"
          title=" "
          disabled={isUploading}
        >
          <Upload className="h-4 w-4" />
        </button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
      />

      <p className="text-xs text-gray-500 text-center">
           <br />
        ( 5MB, JPG/PNG)
      </p>
    </div>
  );
}

export default function MyPage() {
  const { user, updateProfile, isLoading } = useAuth();
  const [editingField, setEditingField] = useState<string | null>(null);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const [localUser, setLocalUser] = useState<UserType | null>(user);

  //      
  React.useEffect(() => {
    if (user) {
      setLocalUser(user);
    }
  }, [user]);

  const handleFieldEdit = useCallback(async (field: string, value: string) => {
    if (editingField === field && value !== '') {
      //  
      try {
        const updateData: Partial<UserType> = { [field]: value };
        const success = await updateProfile(updateData);
        
        if (success) {
          setLocalUser(prev => prev ? { ...prev, [field]: value } : null);
          setEditingField(null);
        } else {
          alert(' .  .');
        }
      } catch (error) {
        console.error('Profile update error:', error);
        alert('   .');
      }
    } else {
      //   
      setEditingField(editingField === field ? null : field);
    }
  }, [editingField, updateProfile]);

  const handleImageChange = useCallback(async (file: File | null) => {
    if (!file) return;

    setIsUploadingImage(true);
    
    try {
      //      .
      //    
      const imageUrl = URL.createObjectURL(file);
      
      //   FormData  
      // const formData = new FormData();
      // formData.append('profile_image', file);
      // const success = await uploadProfileImage(formData);
      
      //   URL 
      setLocalUser(prev => prev ? { ...prev, profile_image: imageUrl } : null);
      
      // TODO:     
      setTimeout(() => {
        setIsUploadingImage(false);
      }, 1000);
      
    } catch (error) {
      console.error('Image upload error:', error);
      alert('  .');
      setIsUploadingImage(false);
    }
  }, []);

  if (isLoading || !localUser) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        {/*  */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center gap-4 mb-6">
            <User className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900"></h1>
              <p className="text-gray-600">    </p>
            </div>
          </div>

          {/*     */}
          <div className="flex justify-center mb-8">
            <ProfileImageUpload
              currentImage={localUser.profile_image}
              onImageChange={handleImageChange}
              isUploading={isUploadingImage}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/*   */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <User className="h-6 w-6 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900"> </h2>
            </div>

            <div className="space-y-6">
              <EditableField
                label=""
                value={localUser.nickname}
                isEditing={editingField === 'nickname'}
                onEdit={(value) => handleFieldEdit('nickname', value)}
                placeholder=" "
              />

              <EditableField
                label=""
                value={localUser.email}
                isEditing={editingField === 'email'}
                onEdit={(value) => handleFieldEdit('email', value)}
                placeholder=" "
                type="email"
              />

              <EditableField
                label=""
                value={localUser.phone || ''}
                isEditing={editingField === 'phone'}
                onEdit={(value) => handleFieldEdit('phone', value)}
                placeholder=" "
                type="tel"
              />

              <EditableField
                label=""
                value={localUser.company || ''}
                isEditing={editingField === 'company'}
                onEdit={(value) => handleFieldEdit('company', value)}
                placeholder=" "
              />
            </div>
          </div>

          {/*   */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <Shield className="h-6 w-6 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900"> </h2>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Mail className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900"> </p>
                    <p className="text-sm text-gray-600">
                      {localUser.email_verified ? ' ' : ' '}
                    </p>
                  </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                  localUser.email_verified 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {localUser.email_verified ? '' : ''}
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Calendar className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900"></p>
                    <p className="text-sm text-gray-600">
                      {localUser.created_at ? new Date(localUser.created_at).toLocaleDateString('ko-KR') : ' '}
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Settings className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900"> </p>
                    <p className="text-sm text-gray-600">
                      {localUser.login_method || ''}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/*   */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-6">
          <div className="flex items-center gap-3 mb-6">
            <Settings className="h-6 w-6 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900"></h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a 
              href="/reset-password" 
              className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            >
              <Key className="h-5 w-5 text-gray-400" />
              <div>
                <p className="font-medium text-gray-900"> </p>
                <p className="text-sm text-gray-600">    </p>
              </div>
            </a>

            <button className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
              <Settings className="h-5 w-5 text-gray-400" />
              <div>
                <p className="font-medium text-gray-900"> </p>
                <p className="text-sm text-gray-600">    </p>
              </div>
            </button>

            <a 
              href="/verify-email" 
              className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            >
              <Mail className="h-5 w-5 text-gray-400" />
              <div>
                <p className="font-medium text-gray-900"> </p>
                <p className="text-sm text-gray-600">   </p>
              </div>
            </a>

            <a 
              href="/find-account" 
              className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            >
              <Search className="h-5 w-5 text-gray-400" />
              <div>
                <p className="font-medium text-gray-900"> </p>
                <p className="text-sm text-gray-600">    </p>
              </div>
            </a>
          </div>
        </div>

        {/*    */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-6">
          <div className="flex items-center gap-3 mb-6">
            <AlertTriangle className="h-6 w-6 text-red-500" />
            <h2 className="text-lg font-semibold text-gray-900"> </h2>
          </div>

          <div className="space-y-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-medium text-red-800 mb-2"> </h3>
                  <p className="text-sm text-red-700 mb-4">
                         . 
                          .
                  </p>
                  <ul className="text-xs text-red-600 space-y-1 mb-4">
                    <li>•    </li>
                    <li>•     </li>
                    <li>•     </li>
                    <li>• 30   </li>
                  </ul>
                  <a 
                    href="/delete-account"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                     
                  </a>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Shield className="h-5 w-5 text-blue-500 mt-0.5" />
                <div>
                  <h3 className="font-medium text-blue-800 mb-2"> </h3>
                  <p className="text-sm text-blue-700 mb-3">
                           .
                  </p>
                  <button 
                    className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                    onClick={() => alert('    .')}
                  >
                    <Settings className="h-4 w-4" />
                     
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}