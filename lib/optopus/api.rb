require 'rubygems'
require 'json'
require 'net/http'
require 'uri'

module Optopus
  class API
    def initialize(endpoint)
      @endpoint = endpoint
    end

    # Search for optopus data, types can be supplied to
    # restrict what data to search through
    def search(string, types=nil)
      path = "/api/search?string=#{URI.escape(string)}"

      if types
        raise 'types must be an Array' unless types.kind_of?(Array)
        path += "&types=#{types.join(',')}"
      end

      get(path)
    end

    private

    def get(path)
      request = Net::HTTP::Get.new(path)
      request['Accept'] = 'application/json'
      response = http.request(request)
      unless response.class == Net::HTTPOK
        raise "Invalid response received: #{response.class} #{response.read_body}"
      end
      JSON.parse(response.read_body)['results']
    end

    def uri
      @uri ||= URI.parse(@endpoint)
    end

    def http
      @http ||= Net::HTTP.new(uri.host, uri.port)
    end
  end
end
