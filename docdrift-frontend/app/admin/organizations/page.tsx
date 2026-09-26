'use client';

import React, { useState, useEffect } from 'react';
import Navigation from '@/components/Navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  getOrganizations, 
  createOrganization, 
  getOrganizationUsers, 
  registerUser 
} from '@/lib/api';

type Organization = {
  id: string;
  name: string;
  admin_count: number;
  employee_count: number;
};

type UserRecord = {
  email: string;
  role: string;
};

export default function MaintainerDashboard() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create Org State
  const [newOrgName, setNewOrgName] = useState('');
  const [creatingOrg, setCreatingOrg] = useState(false);

  // Manage Users State
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);
  const [orgUsers, setOrgUsers] = useState<UserRecord[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);

  // Create User State
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserPassword, setNewUserPassword] = useState('');
  const [newUserRole, setNewUserRole] = useState('admin');
  const [creatingUser, setCreatingUser] = useState(false);
  const [userSuccess, setUserSuccess] = useState<string | null>(null);
  const [userError, setUserError] = useState<string | null>(null);

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    setLoading(true);
    try {
      const data = await getOrganizations();
      setOrganizations(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load organizations.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrg = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newOrgName.trim()) return;
    setCreatingOrg(true);
    setError(null);
    try {
      await createOrganization(newOrgName);
      setNewOrgName('');
      await fetchOrganizations();
    } catch (err: any) {
      setError(err.message || 'Failed to create organization.');
    } finally {
      setCreatingOrg(false);
    }
  };

  const handleSelectOrg = async (org: Organization) => {
    setSelectedOrg(org);
    setLoadingUsers(true);
    setUserError(null);
    setUserSuccess(null);
    try {
      const data = await getOrganizationUsers(org.id);
      setOrgUsers(data);
    } catch (err: any) {
      setOrgUsers([]);
    } finally {
      setLoadingUsers(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOrg || !newUserEmail || !newUserPassword) return;
    setCreatingUser(true);
    setUserError(null);
    setUserSuccess(null);
    try {
      await registerUser(newUserEmail, newUserPassword, newUserRole, selectedOrg.id);
      setUserSuccess(`Successfully created ${newUserRole} account for ${newUserEmail}`);
      setNewUserEmail('');
      setNewUserPassword('');
      // Refresh the users and orgs to update counts
      await handleSelectOrg(selectedOrg);
      await fetchOrganizations();
    } catch (err: any) {
      setUserError(err.message || 'Failed to create user account.');
    } finally {
      setCreatingUser(false);
    }
  };

  return (
    <ProtectedRoute allowedRoles={['maintainer']}>
      <div className="min-h-screen flex flex-col bg-study-bg text-study-text dark:bg-study-bg-dark dark:text-study-text-dark paper-grain transition-colors">
        <Navigation />

        <main className="flex-1 p-4 sm:p-8 md:p-12 max-w-5xl mx-auto w-full space-y-8">
          <header className="border-b border-study-border/70 dark:border-study-border-dark/70 pb-6 flex items-end justify-between">
            <div>
              <h1 className="font-serif text-3xl sm:text-4xl font-semibold text-primary dark:text-[#EDE7D9]">
                Platform Operations
              </h1>
              <p className="text-sm text-study-text/60 dark:text-study-text-dark/60 font-mono mt-2">
                Maintainer Dashboard &bull; Multi-Tenant Administration
              </p>
            </div>
            <div className="hidden sm:flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-mono text-accent">
              <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
              Root Access Active
            </div>
          </header>

          {error && (
            <div className="rounded-lg border border-warning/40 bg-warning/5 p-4 text-sm font-mono text-warning">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            
            {/* LEFT COLUMN: Orgs List */}
            <div className="lg:col-span-2 space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="font-serif text-2xl text-primary dark:text-[#EDE7D9]">Registered Organizations</h2>
                <span className="text-xs font-mono bg-study-border/20 px-2 py-1 rounded">Total: {organizations.length}</span>
              </div>

              {/* Create Org Inline Form */}
              <form onSubmit={handleCreateOrg} className="archive-card rounded-xl p-4 flex flex-col sm:flex-row items-center gap-3 shadow-xs">
                <input
                  type="text"
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                  placeholder="New Organization Name..."
                  className="flex-1 w-full bg-transparent border-b border-study-border dark:border-study-border-dark px-2 py-1.5 text-sm text-study-text dark:text-study-text-dark focus:border-accent focus:outline-none font-sans"
                  disabled={creatingOrg}
                />
                <button
                  type="submit"
                  disabled={!newOrgName.trim() || creatingOrg}
                  className="w-full sm:w-auto rounded-lg bg-accent hover:bg-accent-hover text-[#161A16] px-5 py-2 text-xs font-mono font-medium tracking-wide transition-colors shadow-xs disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {creatingOrg ? 'Creating...' : '+ Register Tenant'}
                </button>
              </form>

              {/* Orgs List */}
              {loading ? (
                <div className="archive-card rounded-xl p-12 text-center text-xs font-mono text-study-text/50">
                  Loading catalog...
                </div>
              ) : organizations.length === 0 ? (
                <div className="archive-card rounded-xl p-12 text-center text-sm font-sans text-study-text/60">
                  No organizations registered in the platform yet.
                </div>
              ) : (
                <div className="space-y-3">
                  {organizations.map((org) => (
                    <div 
                      key={org.id} 
                      onClick={() => handleSelectOrg(org)}
                      className={`archive-card rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between cursor-pointer transition-all border ${
                        selectedOrg?.id === org.id 
                          ? 'border-accent shadow-md bg-accent/5' 
                          : 'border-transparent hover:border-study-border/50 shadow-xs hover:shadow-sm'
                      }`}
                    >
                      <div className="space-y-1">
                        <h3 className="font-semibold text-primary dark:text-[#EDE7D9] text-lg">{org.name}</h3>
                        <p className="text-[10px] font-mono text-study-text/50 uppercase tracking-wide">ID: {org.id}</p>
                      </div>
                      <div className="flex gap-4 mt-3 sm:mt-0">
                        <div className="text-center">
                          <p className="text-xs font-mono text-study-text/60">Admins</p>
                          <p className="font-semibold">{org.admin_count}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs font-mono text-study-text/60">Employees</p>
                          <p className="font-semibold">{org.employee_count}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* RIGHT COLUMN: Org Details / Create User */}
            <div className="lg:col-span-1">
              {!selectedOrg ? (
                <div className="archive-card rounded-xl p-8 text-center border border-dashed border-study-border/50 bg-study-bg/30 h-full flex flex-col items-center justify-center">
                  <div className="h-10 w-10 rounded-full border border-study-border bg-study-border/10 flex items-center justify-center text-study-text/40 mb-3 text-lg font-serif">
                    §
                  </div>
                  <p className="text-xs font-mono text-study-text/50">Select an organization to manage its accounts.</p>
                </div>
              ) : (
                <div className="archive-card rounded-xl p-5 sm:p-6 shadow-md border-t-2 border-t-accent space-y-6">
                  <div className="border-b border-study-border/50 pb-4">
                    <h2 className="font-serif text-xl font-medium text-primary dark:text-[#EDE7D9] break-words">
                      {selectedOrg.name}
                    </h2>
                    <p className="text-[10px] font-mono uppercase tracking-widest text-study-text/50 mt-1">Tenant Management</p>
                  </div>

                  {/* Users List inside Org */}
                  <div className="space-y-3">
                    <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-study-text/70">Current Accounts</h3>
                    {loadingUsers ? (
                      <p className="text-xs font-mono text-study-text/40">Loading accounts...</p>
                    ) : orgUsers.length === 0 ? (
                      <p className="text-xs text-study-text/50 italic font-sans">No users provisioned.</p>
                    ) : (
                      <ul className="space-y-2 max-h-48 overflow-y-auto pr-2">
                        {orgUsers.map((u, i) => (
                          <li key={i} className="flex items-center justify-between text-xs bg-study-border/10 rounded px-2 py-1.5">
                            <span className="font-sans truncate mr-2" title={u.email}>{u.email}</span>
                            <span className={`font-mono uppercase text-[9px] px-1.5 py-0.5 rounded shrink-0 ${u.role === 'admin' ? 'bg-accent/20 text-accent' : 'bg-study-text/10'}`}>
                              {u.role}
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>

                  {/* Provision New User Form */}
                  <form onSubmit={handleCreateUser} className="space-y-4 pt-4 border-t border-study-border/50">
                    <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-study-text/70">Provision Account</h3>
                    
                    {userError && <p className="text-xs text-warning bg-warning/10 p-2 rounded">{userError}</p>}
                    {userSuccess && <p className="text-xs text-green-500 bg-green-500/10 p-2 rounded">{userSuccess}</p>}

                    <div className="space-y-3">
                      <div>
                        <input
                          type="email"
                          required
                          value={newUserEmail}
                          onChange={(e) => setNewUserEmail(e.target.value)}
                          placeholder="Email address"
                          className="w-full rounded bg-study-bg/50 border border-study-border dark:border-study-border-dark px-3 py-2 text-xs focus:border-accent focus:outline-none"
                        />
                      </div>
                      <div>
                        <input
                          type="password"
                          required
                          value={newUserPassword}
                          onChange={(e) => setNewUserPassword(e.target.value)}
                          placeholder="Password"
                          className="w-full rounded bg-study-bg/50 border border-study-border dark:border-study-border-dark px-3 py-2 text-xs focus:border-accent focus:outline-none"
                        />
                      </div>
                      <div className="flex items-center gap-3">
                        <select 
                          value={newUserRole}
                          onChange={(e) => setNewUserRole(e.target.value)}
                          className="flex-1 rounded bg-study-bg/50 border border-study-border dark:border-study-border-dark px-2 py-2 text-xs font-mono uppercase focus:outline-none focus:border-accent"
                        >
                          <option value="admin">Admin</option>
                          <option value="employee">Employee</option>
                        </select>
                        <button
                          type="submit"
                          disabled={!newUserEmail || !newUserPassword || creatingUser}
                          className="rounded bg-accent hover:bg-accent-hover text-[#161A16] px-4 py-2 text-xs font-mono font-medium disabled:opacity-50 transition-colors"
                        >
                          {creatingUser ? '...' : 'Create'}
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
              )}
            </div>

          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
