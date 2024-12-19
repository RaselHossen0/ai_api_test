import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

import {  FaSpinner as Loader2 } from 'react-icons/fa'; // Assuming you're using a loader and play icon from react-icons
import { urls } from '@/api/urls'


// import { useState, useEffect } from 'react';
// import { Button, Progress, Select, SelectItem, SelectTrigger, SelectContent, SelectValue, Label, Card, CardHeader, CardContent, CardTitle, Tabs, TabsList, TabsTrigger, TabsContent } from '@your-design-system';
// import { Play, Loader2 } from 'react-icons/all'; // Assuming you're using a loader and play icon from react-icons

export default function IntegratedTestDashboard() {
  // State for Test Script Creation
  const [framework, setFramework] = useState('postman');
  const [language, setLanguage] = useState('javascript');
  const [generatedScript, setGeneratedScript] = useState('');
  const user: { id: string } = JSON.parse(localStorage.getItem('user') ?? '{}') as { id: string };

  // State for previously fetched APIs
  interface Api {
    id: string;
    api_name: string;
    api_url: string;
    http_method: string;
  }

  const [previousApis, setPreviousApis] = useState<Api[]>([]);
  const [selectedApiId, setSelectedApiId] = useState<string | undefined>(undefined);
  
  const [apiName, setApiName] = useState('');
  const [apiUrl, setApiUrl] = useState('');
  const [httpMethod, setHttpMethod] = useState('GET');


  

  // State for Test Execution
 
 
  

  // State for Test Results

  const [exportFormat, setExportFormat] = useState('html');
  
  // Loading state for script generation
  const [isLoading, setIsLoading] = useState(false);

  // Fetch previous APIs on component mount
  useEffect(() => {
    const fetchPreviousApis = async () => {
      try {
        const response = await fetch(`${urls.baseUrl}/api_management/apis?user_id=${user.id}`, {
          headers: { "Accept": "application/json" },
        });
        const apiData = await response.json();
        setPreviousApis(apiData);
      } catch (err) {
        console.error("Error fetching APIs", err);
      }
    };
    fetchPreviousApis();
  }, [user.id]);


  // Handle API select from the dropdown
  const handleApiSelect = (apiId: string) => {
    const selectedApi = previousApis.find(api => api.id === apiId);
    console.log(apiName, apiUrl, httpMethod);
    if (selectedApi) {
      setApiName(selectedApi.api_name);
      setApiUrl(selectedApi.api_url);
      setHttpMethod(selectedApi.http_method);
      setSelectedApiId(apiId);
    }
  };

  // Function to call the API and generate the test script
  const handleGenerateScript = async () => {
    if (!selectedApiId) {
      alert('Please select an API first!');
      return;
    }
    setIsLoading(true);
    try {
      const response = await fetch(`${urls.baseUrl}/api/script/generate_script?api_id=${selectedApiId}&language=${language}&framework=${framework}`, {
        method: 'POST',
        headers: { 'Accept': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('Failed to generate script');
      }

      const data = await response.json();
      setGeneratedScript(data.script); // Assuming the response contains the generated script in 'script'
    } catch (error) {
      console.error('Error generating script:', error);
      setGeneratedScript('Failed to generate script');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportToGitHub = async () => {
    try {
      const response = await fetch(`${urls.baseUrl}/api/script/export_script`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          owner: user.id,  // The GitHub owner/username
          file_name: `test-script-${Date.now()}.js`,  // Filename with timestamp
          script_content: generatedScript,  // Script content to export
        }),
      });
  
      if (response.ok) {
        const data = await response.json();
        alert(data.message || 'Exported to GitHub successfully!');
      } else {
        const errorData = await response.json();
        console.error('Error exporting to GitHub:', errorData);
        alert(`Failed to export to GitHub: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error exporting to GitHub:', error);
      alert('Failed to export to GitHub');
    }
  };
  

 
  const handleExport = async () => {
    try {
      // Set the MIME type and file extension based on the selected format
      let mimeType, fileExtension;
      switch (exportFormat) {
        case 'html':
          mimeType = 'text/html';
          fileExtension = 'html';
          break;
        case 'pdf':
          mimeType = 'application/pdf';
          fileExtension = 'pdf';
          break;
        case 'json':
          mimeType = 'application/json';
          fileExtension = 'json';
          break;
        default:
          mimeType = 'text/plain';
          fileExtension = 'txt';
      }
  
      // Convert the generated script into a Blob with the chosen MIME type
      const blob = new Blob([generatedScript], { type: mimeType });
      
      // Create a downloadable link for the Blob
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `generated_script.${fileExtension}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
  
      alert(`Report exported as ${fileExtension.toUpperCase()} successfully!`);
    } catch (error) {
      console.error('Error exporting report:', error);
      alert('Failed to export report');
    }
  };
  return (
    <div className="container mx-auto p-4 space-y-8">
      <h1 className="text-3xl font-bold mb-6">API Testing Dashboard</h1>
  
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Create and Execute Test</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              
              <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="previousApi">Select Previous API</Label>
                <select
                  id="previousApi"
                  value={selectedApiId}
                  onChange={(e) => handleApiSelect(e.target.value)}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                  <option value="" disabled>Select an API</option>
                  {previousApis.map(api => (
                    <option key={api.id} value={api.id}>
                      {api.api_name}
                    </option>
                  ))}
                </select>
              </div>
                <div className="space-y-2">
                  <Label htmlFor="framework">Framework</Label>
                  <select
                    id="framework"
                    value={framework}
                    onChange={(e) => setFramework(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="postman">Postman</option>
                    <option value="junit">JUnit</option>
                    <option value="cypress">Cypress</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="language">Language</Label>
                  <select
                    id="language"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="javascript">JavaScript</option>
                    <option value="python">Python</option>
                    <option value="java">Java</option>
                  </select>
                </div>
                   {/* Dropdown for Selecting Previous API */}
           
              </div>
  
           
  
              <Button onClick={handleGenerateScript} disabled={isLoading}>
                {isLoading ? <Loader2 className="animate-spin h-5 w-5" /> : 'Generate Script'}
              </Button>
  
              <div className="relative">
                <Tabs defaultValue="preview">
                  <div className="flex justify-between items-center">
                    <TabsList>
                      <TabsTrigger value="preview">Preview</TabsTrigger>
                      <TabsTrigger value="edit">Edit</TabsTrigger>
                    </TabsList>
                    <div className="flex space-x-4">
                      <select
                        id="exportFormat"
                        value={exportFormat}
                        onChange={(e) => setExportFormat(e.target.value)}
                        className="block w-32 pl-3 pr-10 py-1.5 text-sm border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 rounded-md"
                      >
                        <option value="pdf">PDF</option>
                        <option value="html">HTML</option>
                        <option value="json">JSON</option>
                      </select>
                      <Button size="sm" onClick={handleExport}>
                        Export ({exportFormat.toUpperCase()})
                      </Button>
                      <Button size="sm" onClick={handleExportToGitHub}>
                        Export to GitHub
                      </Button>
                    </div>
                  </div>
                  <TabsContent value="preview">
                    <pre className="p-4 bg-gray-900 text-white rounded-md overflow-auto max-h-[300px]">
                      {generatedScript || 'No script generated yet.'}
                    </pre>
                  </TabsContent>
                  <TabsContent value="edit">
                    <textarea
                      className="w-full h-[300px] p-4 font-mono text-sm bg-gray-900 text-white border rounded-md"
                      value={generatedScript}
                      onChange={(e) => setGeneratedScript(e.target.value)}
                      placeholder="Edit your generated script here..."
                    />
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}