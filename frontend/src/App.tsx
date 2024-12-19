import React from 'react'
import { useState } from 'react'
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom'
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { BarChart, Upload, Settings, List } from "lucide-react"
import {  useLocation } from 'react-router-dom';



import ConfigureTests from './dashboard/configure-api'

import Settings1 from './dashboard/settings'


const Sidebar = () => {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(true); // Sidebar toggles on mobile

  const handleLogout = () => {
    localStorage.clear();
    sessionStorage.clear();
    document.cookie.split(';').forEach((c) => {
      document.cookie = c
        .replace(/^ +/, '')
        .replace(/=.*/, '=;expires=' + new Date().toUTCString() + ';path=/');
    });
    window.location.href = '/';
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="flex">
      {/* Hamburger Button for Mobile View */}
      <button
        className="absolute top-4 left-4 z-20 md:hidden text-white py-2 px-3 rounded-lg bg-gray-800"
        onClick={() => setIsOpen(!isOpen)}
      >
        <List className="h-6 w-6" />
      </button>

      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 z-10 h-full bg-gray-800 text-white w-64 transform transition-transform duration-300 md:relative ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="space-y-4 py-4">
          <h2 className="px-4 text-lg font-semibold tracking-tight">AI API Testing Tool</h2>
          <div className="space-y-1 px-4">
            <Button
              asChild
              variant="ghost"
              className={`w-full justify-start ${
                isActive('/generate-test') ? 'bg-gray-700' : 'hover:bg-gray-700'
              }`}
            >
              <Link to="/generate-test" className="flex items-center">
                <Upload className="mr-2 h-4 w-4" />
                Generate Test
              </Link>
            </Button>
            <Button
              asChild
              variant="ghost"
              className={`w-full justify-start ${
                isActive('/scripts') ? 'bg-gray-700' : 'hover:bg-gray-700'
              }`}
            >
              <Link to="/scripts" className="flex items-center">
                <BarChart className="mr-2 h-4 w-4" />
                Scripts
              </Link>
            </Button>
            <Button
              asChild
              variant="ghost"
              className={`w-full justify-start ${
                isActive('/settings') ? 'bg-gray-700' : 'hover:bg-gray-700'
              }`}
            >
              <Link to="/settings" className="flex items-center">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </Link>
            </Button>
            <Button
              asChild
              variant="ghost"
              className="w-full justify-start hover:bg-gray-700"
              onClick={handleLogout}
            >
              <div className="flex items-center cursor-pointer">
                <List className="mr-2 h-4 w-4" />
                Logout
              </div>
            </Button>
          </div>
        </div>
      </div>

      {/* Overlay for Mobile View */}
      {isOpen && (
        <div
          className="fixed inset-0 z-0 bg-black opacity-50 md:hidden"
          onClick={() => setIsOpen(false)}
        ></div>
      )}
    </div>
  );
};





// export default Sidebar;

import SignIn from './auth/SignIn'
import SignUp from './auth/SignUp'
import { urls } from './api/urls'
import IntegratedTestDashboard from './dashboard/test-script'

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  React.useEffect(() => {
    const savedAuthState = localStorage.getItem('access_token');
    if (savedAuthState) {
      fetch(urls.getCurrentUser, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${savedAuthState}`,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data?.message) {
            localStorage.removeItem('access_token');
            setIsAuthenticated(false);
          } else {
            setIsAuthenticated(true);
          }
        })
        .catch(() => setIsAuthenticated(false));
    } else {
      setIsAuthenticated(false);
    }
  }, []);

  if (isAuthenticated === null) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <Router>
      {isAuthenticated ? (
        <div className="flex h-screen">
          <Sidebar />
          <Separator orientation="vertical" />
          <ScrollArea className="flex-1 p-4">
            <Routes>
              <Route path="/generate-test" element={<ConfigureTests />} />
              <Route path="/settings" element={<Settings1 />} />
              <Route path="/scripts" element={<IntegratedTestDashboard />} />
            </Routes>
          </ScrollArea>
        </div>
      ) : (
        <div className="flex items-center justify-center h-screen bg-gray-100">
          <Routes>
            <Route path="/signin" element={<SignIn />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/" element={<SignUp />} />
          </Routes>
        </div>
      )}
    </Router>
  );
}
