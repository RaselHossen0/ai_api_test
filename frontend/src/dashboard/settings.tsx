import React, { useState ,useEffect} from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { GitBranch, User, Mail, Key } from "lucide-react"
import { urls } from '@/api/urls'

export default function Settings() {
  const [name, setName] = useState('John Doe')
  const [email, setEmail] = useState('john.doe@example.com')
  const [userId, setUserId] = useState('JD123456')

  const [githubRepo, setGithubRepo] = useState('')
  const [githubToken, setGithubToken] = useState('')

  const user =JSON.parse(localStorage.getItem('user')??'{}');
  const [newPassword, setNewPassword] = useState(''); // Local state for password
 


  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Prepare the user data to send in the request
    const updatedProfile: { name: string; email: string; password?: string } = {
      name,
      email
    };
    if (newPassword!== '') {
      updatedProfile['password'] = newPassword;
    }

  
    try {
      const response = await fetch(`${urls.baseUrl}/users/edit/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedProfile), // Send the updated user profile as the body
      });
  
      if (response.ok) {
        const data = await response.json();
        console.log('Profile updated successfully:', data);
        localStorage.setItem('user',JSON.stringify(data));
        alert('Profile updated successfully!');
      } else {
        const errorData = await response.json();
        console.error('Failed to update profile:', errorData.detail);
        alert('Failed to update profile');
      }
    } catch (error) {
      console.error('Error while saving profile:', error);
      alert('An error occurred while updating the profile');
    }
  };
  // Handler to save GitHub details by calling the FastAPI endpoint
  interface GitHubDetails {
    owner: string;
    repo: string;
    access_token: string;
  }
  const [detailsFetched, setDetailsFetched] = useState(false); // New state to track if fetched


  useEffect(() => {
    
    if (!detailsFetched)
    {
      fetchGitHubDetails();
      setUserId(user.id);
      setEmail(user.email);
      setName(user.name);
    }
    
  }, [ detailsFetched]);
  const fetchGitHubDetails = async () => {
    try {
      const response = await fetch(`${urls.baseUrl}/api/script/get_github_details?owner=${user.id}`);
      console.log(response);
      if (!response.ok) throw new Error("GitHub details not found");
      
      const data = await response.json();
      setGithubRepo(`${data.repo}`);
      setGithubToken(data.access_token);
      setDetailsFetched(true);
      // alert("GitHub details fetched successfully!");
    } catch (error) {
      console.error("Error fetching GitHub details:", error);
      alert("Failed to fetch GitHub details");
    }
  };
    // Edit GitHub Details
    const handleEditGitHub = async () => {
      try {
        // const [owner, repo] = githubRepo.split("/");
        const response = await fetch(`${urls.baseUrl}/api/script/edit_github_details`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            owner: user.id,
            repo: githubRepo,
            access_token: githubToken,
          }),
        });
        if (!response.ok) throw new Error("Failed to update GitHub details");
  
        alert("GitHub details updated successfully!");
      } catch (error) {
        console.error("Error updating GitHub details:", error);
        alert("Failed to update GitHub details");
      }
    };

  const handleSaveGitHub = async (e: React.FormEvent) => {
    e.preventDefault();

    // const [owner, repo] = githubRepo.replace('https://github.com/', '').split('/');
    const githubDetails: GitHubDetails = {
      owner: user.id,
      repo: githubRepo,
      access_token: githubToken,
    };

    try {
      const response = await fetch(`${urls.baseUrl}/api/script/save_github_details`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(githubDetails),
      });

      if (response.ok) {
        alert('GitHub settings saved successfully!');
      } else {
        const errorData = await response.json();
        alert(`Failed to save GitHub settings: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error saving GitHub settings:', error);
      alert('An error occurred while saving GitHub settings.');
    }
  };

 

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>
      <Tabs defaultValue="profile" className="space-y-6 ">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="profile" >Profile</TabsTrigger>
          <TabsTrigger value="github">GitHub</TabsTrigger>
          
        </TabsList>
        <TabsContent value="profile">
        <Card>
      <CardHeader>
        <CardTitle>Profile Settings</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSaveProfile} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-sm font-medium">
              <User className="w-4 h-4 inline-block mr-2" />
              Full Name
            </Label>
            <Input
              id="name"
              value={name} // Bind to the state
              onChange={(e) => setName(e.target.value)} // Update state on change
              className="max-w-md"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm font-medium">
              <Mail className="w-4 h-4 inline-block mr-2" />
              Email Address
            </Label>
            <Input
              id="email"
              type="email"
              value={email} // Bind to the state
              onChange={(e) => setEmail(e.target.value)} // Update state on change
              className="max-w-md"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="userId" className="text-sm font-medium">
              <Key className="w-4 h-4 inline-block mr-2" />
              User ID
            </Label>
            <Input
              id="userId"
              value={userId} // Bind to the state
              onChange={(e) => setUserId(e.target.value)} // Update state on change
              className="max-w-md"
              disabled // Make user ID input read-only
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="newPassword" className="text-sm font-medium">
              <Key className="w-4 h-4 inline-block mr-2" />
              New Password (optional)
            </Label>
            <Input
              id="newPassword"
              type="password"
              value={newPassword} // Bind to the state
              onChange={(e) => setNewPassword(e.target.value)} // Update state on change
              className="max-w-md"
            />
          </div>
          <Button type="submit">Save Profile</Button>
        </form>
      </CardContent>
    </Card>
        </TabsContent>
        <TabsContent value="github">
        <Card>
      <CardHeader>
        <CardTitle>GitHub Integration</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSaveGitHub} className="space-y-4">
         
          { (
            <>
              <div className="space-y-2">
                <Label htmlFor="github-repo">GitHub Repository URL</Label>
                <Input 
                  id="github-repo" 
                  value={githubRepo}
                  onChange={(e) => setGithubRepo(e.target.value)}
                  placeholder="username/repo" 
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="github-token">GitHub Access Token</Label>
                <Input 
                  id="github-token" 
                  type="password" 
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  placeholder="Enter your GitHub access token" 
                />
              </div>
              <div className="space-y-4 x-5">
                <Button type="submit">
                  <GitBranch className="" /> Save GitHub Settings
                </Button>
                <Button onClick={handleEditGitHub} variant="secondary" className='ml-4'>
                  Edit GitHub Settings
                </Button>
              </div>
            </>
          )}
        </form>
      </CardContent>
    </Card>
        </TabsContent>
       
      </Tabs>
      
    </div>
  )
}