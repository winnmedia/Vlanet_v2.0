'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Spinner } from '@/components/ui/Spinner';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  avatar?: string;
  lastActive: string;
  projectsCount: number;
}

interface Team {
  id: string;
  name: string;
  description: string;
  members: TeamMember[];
  createdAt: string;
}

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [newMemberEmail, setNewMemberEmail] = useState('');

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        //    API 
        const response = await fetch('/api/projects/', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            ...(localStorage.getItem('token') && {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            })
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        //       
        const projects = await response.json();
        
        // Fallback   
        const mockTeam: Team = {
          id: 'team-1',
          name: 'VideoPlanet Team',
          description: '     ',
          members: [
            {
              id: 'member-1',
              name: '',
              email: 'admin@videoplaetwins.com',
              role: 'owner',
              lastActive: ' ',
              projectsCount: projects?.results?.length || 0
            }
          ],
          createdAt: new Date().toISOString()
        };

        setTeams([mockTeam]);
      } catch (err) {
        console.error('Teams fetch error:', err);
        setError(err instanceof Error ? err.message : '    .');
        
        // Fallback 
        setTeams([{
          id: 'team-1',
          name: 'VideoPlanet Team',
          description: '     ',
          members: [],
          createdAt: new Date().toISOString()
        }]);
      } finally {
        setLoading(false);
      }
    };

    fetchTeams();
  }, []);

  const handleInviteMember = async () => {
    if (!newMemberEmail.trim()) return;

    try {
      const response = await fetch('/api/projects/invite/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(localStorage.getItem('token') && {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          })
        },
        body: JSON.stringify({ email: newMemberEmail })
      });

      if (response.ok) {
        setNewMemberEmail('');
        setShowInviteModal(false);
        //  
        alert('  .');
      } else {
        throw new Error('  .');
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : '    .');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner />
        <span className="ml-3 text-lg">   ...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Team Management</h1>
            <p className="text-gray-600">    .</p>
          </div>
          <button
            onClick={() => setShowInviteModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
             
          </button>
        </div>
        
        {error && (
          <div className="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-700">
            <p className="font-medium"></p>
            <p>{error}</p>
            <p className="text-sm mt-1">   .</p>
          </div>
        )}
      </div>

      <div className="space-y-6">
        {teams.map((team) => (
          <Card key={team.id} className="p-6 bg-white shadow-sm">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">{team.name}</h2>
              <p className="text-gray-600">{team.description}</p>
            </div>

            <div className="mb-4">
              <h3 className="text-lg font-medium text-gray-900 mb-3">
                 ({team.members.length})
              </h3>
              
              {team.members.length > 0 ? (
                <div className="space-y-3">
                  {team.members.map((member) => (
                    <div key={member.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        <div className="h-10 w-10 bg-gray-300 rounded-full flex items-center justify-center mr-3">
                          <span className="text-sm font-medium text-gray-700">
                            {member.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{member.name}</p>
                          <p className="text-xs text-gray-500">{member.email}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-4">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          member.role === 'owner' ? 'bg-purple-100 text-purple-700' :
                          member.role === 'admin' ? 'bg-blue-100 text-blue-700' :
                          member.role === 'member' ? 'bg-green-100 text-green-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {member.role === 'owner' ? '' :
                           member.role === 'admin' ? '' :
                           member.role === 'member' ? '' : ''}
                        </span>
                        <span className="text-xs text-gray-500">{member.lastActive}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8"> .  .</p>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/*   */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4"> </h3>
            <input
              type="email"
              placeholder="  "
              value={newMemberEmail}
              onChange={(e) => setNewMemberEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowInviteModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                
              </button>
              <button
                onClick={handleInviteMember}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                 
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}