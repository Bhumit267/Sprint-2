'use client';

import React, { useState, useEffect } from 'react';
import Navigation from '@/components/Navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { getCurrentUser, getOrganizationUsers, registerUser } from '@/lib/api';

type UserRecord = {
  email: string;
  role: string;
};

export default function OrganizationPage() {
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Invite state (Admin only)
  const [inviteEmail, setInviteEmail] = useState('');
  const [invitePassword, setInvitePassword] = useState('');
  const [inviteRole, setInviteRole] = useState('employee');
  const [inviting, setInviting] = useState(false);
  const [inviteSuccess, setInviteSuccess] = useState<string | null>(null);
  const [inviteError, setInviteError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const user = await getCurrentUser();
      if (!user || !user.org_id) throw new Error('Could not identify your organization');
      setCurrentUser(user);

      const orgUsers = await getOrganizationUsers(user.org_id);
      setUsers(orgUsers);
    } catch (err: any) {
      setError(err.message || 'Failed to load organization data');
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser || !currentUser.org_id) return;
    setInviting(true);
    setInviteError(null);
    setInviteSuccess(null);
    
    try {
      await registerUser(inviteEmail, invitePassword, inviteRole, currentUser.org_id);
      setInviteSuccess(`Successfully created ${inviteRole} account for ${inviteEmail}`);
      setInviteEmail('');
      setInvitePassword('');
      // Refresh the list
      const orgUsers = await getOrganizationUsers(currentUser.org_id);
      setUsers(orgUsers);
    } catch (err: any) {
      setInviteError(err.message || 'Failed to invite user');
    } finally {
      setInviting(false);
    }
  };

  const isAdmin = currentUser?.role === 'admin';

  return (
    <ProtectedRoute allowedRoles={['admin', 'employee']}>
      <div className="min-h-screen flex flex-col bg-study-bg text-study-text dark:bg-study-bg-dark dark:text-study-text-dark paper-grain transition-colors">
        <Navigation />

        <main className="flex-1 p-4 sm:p-8 md:p-12 max-w-4xl mx-auto w-full space-y-8">
          <header className="border-b border-study-border/70 dark:border-study-border-dark/70 pb-6">
            <h1 className="font-serif text-3xl sm:text-4xl font-semibold text-primary dark:text-[#EDE7D9]">
              {currentUser?.org_name || 'Organization'}
            </h1>
            <p className="text-sm text-study-text/60 dark:text-study-text-dark/60 font-mono mt-2">
              Team Members & Settings
            </p>
          </header>

          {error && (
            <div className="rounded-lg border border-warning/40 bg-warning/5 p-4 text-sm font-mono text-warning">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            
            {/* LEFT COLUMN: Members List */}
            <div className="lg:col-span-2 space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="font-serif text-2xl text-primary dark:text-[#EDE7D9]">Members</h2>
                <span className="text-xs font-mono bg-study-border/20 px-2 py-1 rounded">Total: {users.length}</span>
              </div>

              {loading ? (
                <div className="archive-card rounded-xl p-12 text-center text-xs font-mono text-study-text/50">
                  Loading members...
                </div>
              ) : (
                <div className="archive-card rounded-xl overflow-hidden">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-study-border/50 bg-study-border/5 text-[10px] uppercase tracking-wider font-mono text-study-text/60">
                        <th className="p-4 font-medium">User Email</th>
                        <th className="p-4 font-medium">Role</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-study-border/30">
                      {users.map((u, i) => (
                        <tr key={i} className="hover:bg-study-border/5 transition-colors">
                          <td className="p-4 text-sm font-sans flex items-center gap-3">
                            {u.email}
                            {u.email === currentUser?.email && (
                              <span className="text-[9px] font-mono bg-accent/10 text-accent px-1.5 py-0.5 rounded">You</span>
                            )}
                          </td>
                          <td className="p-4">
                            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[10px] font-mono uppercase tracking-wider ${
                              u.role === 'admin' 
                                ? 'bg-warning/10 text-warning border border-warning/20' 
                                : 'bg-study-text/5 dark:bg-study-text-dark/5 text-study-text/80 dark:text-study-text-dark/80 border border-study-border/40 dark:border-study-border-dark/40'
                            }`}>
                              {u.role === 'admin' && <span className="w-1.5 h-1.5 rounded-full bg-warning" />}
                              {u.role}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* RIGHT COLUMN: Invite Member */}
            {isAdmin && (
              <div className="lg:col-span-1">
                <div className="archive-card rounded-xl p-6 shadow-md border-t-2 border-t-accent space-y-5">
                  <div className="border-b border-study-border/50 pb-3">
                    <h2 className="font-serif text-xl font-medium text-primary dark:text-[#EDE7D9]">
                      Invite Member
                    </h2>
                  </div>

                  <form onSubmit={handleInvite} className="space-y-4">
                    {inviteError && <p className="text-xs text-warning bg-warning/10 p-2 rounded">{inviteError}</p>}
                    {inviteSuccess && <p className="text-xs text-green-500 bg-green-500/10 p-2 rounded">{inviteSuccess}</p>}

                    <div className="space-y-3">
                      <div>
                        <label className="block text-[10px] font-mono uppercase text-study-text/60 mb-1">Email</label>
                        <input
                          type="email"
                          required
                          value={inviteEmail}
                          onChange={(e) => setInviteEmail(e.target.value)}
                          className="w-full rounded bg-study-bg/50 border border-study-border px-3 py-2 text-xs focus:border-accent focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] font-mono uppercase text-study-text/60 mb-1">Temporary Password</label>
                        <input
                          type="password"
                          required
                          value={invitePassword}
                          onChange={(e) => setInvitePassword(e.target.value)}
                          className="w-full rounded bg-study-bg/50 border border-study-border px-3 py-2 text-xs focus:border-accent focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] font-mono uppercase text-study-text/60 mb-1">Role</label>
                        <select 
                          value={inviteRole}
                          onChange={(e) => setInviteRole(e.target.value)}
                          className="w-full rounded bg-study-bg/50 border border-study-border px-3 py-2 text-xs font-mono uppercase focus:outline-none focus:border-accent"
                        >
                          <option value="employee">Employee</option>
                          <option value="admin">Admin</option>
                        </select>
                      </div>
                      
                      <button
                        type="submit"
                        disabled={!inviteEmail || !invitePassword || inviting}
                        className="w-full mt-2 rounded bg-accent hover:bg-accent-hover text-[#161A16] px-4 py-2.5 text-xs font-mono font-medium disabled:opacity-50 transition-colors shadow-xs"
                      >
                        {inviting ? 'Inviting...' : 'Send Invitation'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
