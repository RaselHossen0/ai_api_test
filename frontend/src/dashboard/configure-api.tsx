import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

import {  Play } from "lucide-react";
import { urls } from "@/api/urls";

interface TestResult {
  description: string;
  expected_status: number;
  status_code: number;
  success: boolean;
  response_data: any;
  test_case: {
    description: string;
    expected_status: number;
    test_type: string;
    payload?: any;
  };
  headers: Record<string, string>;
}

interface Api {
  id: string;
  api_name: string;
  api_url: string;
  http_method: string;
  user_id: string;
  payload?: Record<string, any>;
  parameters?: Record<string, any>;
  headers?: Record<string, any>;
  created_at?: string;
}

export default function ConfigureTests() {
  const [apiName, setApiName] = useState("");
  const [apiUrl, setApiUrl] = useState("");
  const [httpMethod, setHttpMethod] = useState("GET");

  // const [testName, setTestName] = useState("");
  // const [testDescription, setTestDescription] = useState("");
  const [testParams, setTestParams] = useState("");
  const [testHeaders, setTestHeaders] = useState("");
  const [testPayload, setTestPayload] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<TestResult[]>([]);
 
  const [previousApis, setPreviousApis] = useState<Api[]>([]);
  const [selectedApiId, setSelectedApiId] = useState("");

  const user = JSON.parse(localStorage.getItem("user") || "{}");

  useEffect(() => {
    // Fetch previous APIs on component mount
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

  const handleApiSelect = (apiId: string) => {
    const selectedApi = previousApis.find(api => api.id === apiId);
    if (selectedApi) {
      setApiName(selectedApi.api_name);
      setApiUrl(selectedApi.api_url);
      setHttpMethod(selectedApi.http_method);
      setSelectedApiId(apiId);
      setTestHeaders(JSON.stringify(selectedApi.headers || {}, null, 2));
      setTestParams(JSON.stringify(selectedApi.parameters || {}, null, 2));
      setTestPayload(JSON.stringify(selectedApi.payload || {}, null, 2));
      
    }
  };

  const handleAddAndRunTest = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const payload = {
        api_name: apiName,
        api_url: apiUrl,
        http_method: httpMethod,
        headers: JSON.parse(testHeaders || "{}"),
        parameters: JSON.parse(testParams || "{}"),
        payload: JSON.parse(testPayload || "{}"),
        user_id: user.id,
        is_previous: selectedApiId!="" ? true : false,
      };

      const testResponse = await fetch(urls.uploadIndividualAPI, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const responseData = await testResponse.json();
      console.log(responseData);
      const headers = Array.from(testResponse.headers.entries()).reduce((acc, [key, value]) => ({ ...acc, [key]: value }), {});

      setResults([{
        description: '',
        expected_status: 200,
        status_code: testResponse.status,
        success: testResponse.status === 200,
        response_data: responseData,
        test_case: {
          description: '',
          expected_status: 200,
          test_type: "API",
        },
        headers,
      }]);
    } catch (err) {
      setError("An error occurred while uploading or testing the API.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Configure Tests and Add API</h1>
      <Card>
        <CardHeader>
          <CardTitle>API and Test Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAddAndRunTest} className="space-y-4">
            {/* Row for API Selection */}
            <div className="space-y-2">
              <Label htmlFor="api-select">Select Previous API</Label>
              <select
                id="api-select"
                className="w-full p-2 border rounded"
                value={selectedApiId}
                onChange={(e) => handleApiSelect(e.target.value)}
              >
                <option value="">Select an API</option>
                {previousApis.map(api => (
                  <option key={api.id} value={api.id}>{api.api_name}</option>
                ))}
              </select>
            </div>
  
            {/* Row for Small Fields */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="api-name">API Name</Label>
                <Input
                  id="api-name"
                  value={apiName}
                  onChange={(e) => setApiName(e.target.value)}
                  placeholder="Enter API name"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="api-url">API URL</Label>
                <Input
                  id="api-url"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  placeholder="https://api.example.com/endpoint"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="api-method">HTTP Method</Label>
                <select
                  id="api-method"
                  className="w-full p-2 border rounded"
                  value={httpMethod}
                  onChange={(e) => setHttpMethod(e.target.value)}
                >
                  <option>GET</option>
                  <option>POST</option>
                  <option>PUT</option>
                  <option>DELETE</option>
                </select>
              </div>
            </div>
  
            {/* Other Fields */}
          
            <TextareaField id="test-params" label="Parameters" value={testParams} setValue={setTestParams} placeholder="Enter test parameters (JSON format)" />
            <TextareaField id="test-headers" label="Headers" value={testHeaders} setValue={setTestHeaders} placeholder="Enter request headers (JSON format)" />
            <TextareaField id="test-payload" label="Payload" value={testPayload} setValue={setTestPayload} placeholder="Enter request payload (JSON format)" />
  
            {/* Submit Button */}
            <div className="flex space-x-2 mb-3 py-5">
              <Button type="submit" variant="secondary">
                {loading ? "Loading..." : <><Play className="mr-2 h-4 w-4" /> Add API & Run Test</>}
              </Button>
            </div>
          </form>
  
          {/* Render Results */}
          {results.length > 0 ? (
            results.map((result) => (
              result.response_data ? (
                result.response_data.map && result.response_data.map((res: any, i: number) => (
                  <ResultDisplay key={i} result={res} />
                ))
              ) : (
                <div className="text-gray-500 mt-4">No test results to display.</div>
              )

            ))
          ) : (
            <div className="text-gray-500 mt-4">No test results to display.</div>
          )}
          {error && <div className="text-red-500 mt-2"><strong>Error:</strong> {error}</div>}
        </CardContent>
      </Card>
    </div>
  );
}



function TextareaField({ id, label, value, setValue, placeholder }: { id: string; label: string; value: string; setValue: React.Dispatch<React.SetStateAction<string>>; placeholder: string }) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <Textarea id={id} value={value} onChange={(e) => setValue(e.target.value)} placeholder={placeholder} />
    </div>
  );
}

function ResultDisplay({ result }: { result: TestResult }) {
  return (
    <div className={`p-4 mb-4 rounded ${result.success ? 'bg-green-100' : 'bg-red-100'}`}>
      <h3 className="font-semibold text-lg">{result.test_case.description || 'Test Results'}</h3>
      <div className="space-y-1">
        <p><strong>Expected Status:</strong> {result.test_case.expected_status}</p>
        <p><strong>Actual Status:</strong> {result.status_code}</p>
        <p><strong>Success:</strong> {result.success ? '✅' : '❌'}</p>
      </div>
      <div className="mt-4">
        <h4 className="font-semibold text-blue-600">Test Details</h4>
        <p><strong>Test Type:</strong> {result.test_case.test_type}</p>
        <p><strong>Payload:</strong></p>
        <pre className="whitespace-pre-wrap bg-gray-100 p-2 rounded overflow-auto max-h-64">{JSON.stringify(result.test_case.payload, null, 2)}</pre>
      </div>
      <div className="mt-4">
        <h4 className="font-semibold text-blue-600">Response Data</h4>
        <pre className="whitespace-pre-wrap bg-gray-100 p-2 rounded">{JSON.stringify(result.response_data, null, 2)}</pre>
      </div>
      {/* <div className="mt-4">
        <h4 className="font-semibold text-blue-600">Headers</h4>
        <pre className="whitespace-pre-wrap bg-gray-100 p-2 rounded">{JSON.stringify(result.headers, null, 2)}</pre>
      </div> */}
    </div>
  );
}
